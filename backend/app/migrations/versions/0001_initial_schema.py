"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-06-16 15:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Auth & Identity ──
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('activity_profile', sa.Float(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index(op.f('ix_sessions_ip_address'), 'sessions', ['ip_address'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # ── Traffic & Features (Partitioned) ──
    # Note: Alembic doesn't natively support creating partitioned tables with op.create_table easily
    # so we use raw SQL for the partitioned tables.
    
    op.execute("""
        CREATE TABLE raw_events (
            id UUID NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            ip_address VARCHAR(45) NOT NULL,
            session_id VARCHAR(64),
            user_id VARCHAR(64),
            method VARCHAR(10) NOT NULL,
            endpoint VARCHAR(2048) NOT NULL,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50) NOT NULL,
            status_code INTEGER NOT NULL,
            response_time FLOAT NOT NULL,
            request_size INTEGER NOT NULL,
            response_size INTEGER NOT NULL,
            country VARCHAR(2),
            device VARCHAR(50),
            browser VARCHAR(255),
            is_attack BOOLEAN NOT NULL,
            attack_type VARCHAR(50) NOT NULL,
            PRIMARY KEY (id, timestamp)
        ) PARTITION BY RANGE (timestamp);
    """)
    op.create_index('ix_raw_events_ip_timestamp', 'raw_events', ['ip_address', 'timestamp'])
    op.create_index('ix_raw_events_session_id', 'raw_events', ['session_id'])
    op.create_index('ix_raw_events_user_id', 'raw_events', ['user_id'])

    op.execute("""
        CREATE TABLE features (
            id UUID NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(255) NOT NULL,
            requests_per_minute FLOAT NOT NULL,
            failed_login_rate FLOAT NOT NULL,
            avg_response_time FLOAT NOT NULL,
            endpoint_entropy FLOAT NOT NULL,
            session_duration FLOAT NOT NULL,
            country_switch_frequency FLOAT NOT NULL,
            unique_user_agents INTEGER NOT NULL,
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
    """)
    op.create_index('ix_features_entity_time', 'features', ['entity_type', 'entity_id', 'created_at'])

    # ── Anomalies & Incidents ──
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('assignee', sa.String(length=128), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )

    op.create_table(
        'rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('condition', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('action', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index(op.f('ix_rules_name'), 'rules', ['name'], unique=True)

    op.create_table(
        'anomalies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('detection_method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('source_ip', sa.String(length=45), nullable=True),
        sa.Column('affected_endpoint', sa.String(length=2048), nullable=True),
        sa.Column('event_count', sa.Integer(), nullable=False),
        sa.Column('raw_details', sa.Text(), nullable=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('feature_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='SET NULL')
    )

    op.create_table(
        'investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('incident_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', sa.String(length=128), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('findings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ondelete='CASCADE')
    )

    # Example: Create an initial partition for current month just so inserts don't fail
    op.execute("""
        CREATE TABLE raw_events_default PARTITION OF raw_events DEFAULT;
        CREATE TABLE features_default PARTITION OF features DEFAULT;
    """)


def downgrade() -> None:
    op.drop_table('investigations')
    op.drop_table('anomalies')
    op.drop_table('rules')
    op.drop_table('incidents')
    op.execute("DROP TABLE features CASCADE")
    op.execute("DROP TABLE raw_events CASCADE")
    op.drop_table('sessions')
    op.drop_table('users')
