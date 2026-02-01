"""initial

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # API Keys
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('key_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Conversations
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Messages
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Cards
    op.create_table(
        'cards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id'), nullable=True),
        sa.Column('card_type', sa.String(20), nullable=False),
        sa.Column('front', sa.Text(), nullable=False),
        sa.Column('back', sa.Text(), nullable=False),
        sa.Column('ease_factor', sa.Float(), server_default='2.5'),
        sa.Column('interval', sa.Integer(), server_default='0'),
        sa.Column('repetitions', sa.Integer(), server_default='0'),
        sa.Column('next_review', sa.Date(), server_default=sa.func.current_date()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # Review Logs
    op.create_table(
        'review_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('card_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cards.id'), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('review_logs')
    op.drop_table('cards')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('api_keys')
    op.drop_table('users')
