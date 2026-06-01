"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("deleted_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("products", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(180), nullable=False), sa.Column("sku", sa.String(80), nullable=False), sa.Column("description", sa.Text()), sa.Column("unit_price", sa.Numeric(12, 2), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("low_stock_threshold", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("deleted_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("sku", name="uq_products_sku"))
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_table("customers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(180), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("company", sa.String(180)), sa.Column("phone", sa.String(40)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("deleted_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("email", name="uq_customers_email"))
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_number", sa.String(32), nullable=False), sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("total_amount", sa.Numeric(12, 2), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("deleted_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("order_number"))
    op.create_index("ix_orders_created_at", "orders", ["created_at"])
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_table("order_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.Column("unit_price", sa.Numeric(12, 2), nullable=False), sa.Column("line_total", sa.Numeric(12, 2), nullable=False))
    op.create_table("idempotency_records", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("key", sa.String(255), nullable=False), sa.Column("request_hash", sa.String(64), nullable=False), sa.Column("response_body", sa.Text(), nullable=False), sa.Column("status_code", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.UniqueConstraint("user_id", "key", name="uq_idempotency_user_key"))
    op.create_table("audit_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.Integer(), nullable=False), sa.Column("action", sa.String(80), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("idempotency_records")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("products")
    op.drop_table("users")
