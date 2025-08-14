"""Insert commons datas

Revision ID: 1b3a6c9000d6
Revises: e501a0a11a86
Create Date: 2025-08-12 11:58:47.668093

"""

import datetime
from typing import Sequence, Union
from zoneinfo import ZoneInfo

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b3a6c9000d6"
down_revision: Union[str, Sequence[str], None] = "e501a0a11a86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa

KST = ZoneInfo("Asia/Seoul")


def upgrade():
    """Upgrade schema."""
    now = datetime.datetime.now(KST)

    # regions
    op.bulk_insert(
        sa.table(
            "regions",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "서울"},
            {"created_at": now, "name": "서울 서부(홍대, 합정 부근)"},
            {"created_at": now, "name": "서울 동부(건대 부근)"},
            {"created_at": now, "name": "서울 남부(사당 부근)"},
            {"created_at": now, "name": "서울 북부(종로 부근)"},
            {"created_at": now, "name": "인천"},
            {"created_at": now, "name": "부산"},
            {"created_at": now, "name": "대구"},
            {"created_at": now, "name": "광주"},
            {"created_at": now, "name": "대전"},
            {"created_at": now, "name": "울산"},
            {"created_at": now, "name": "제주"},
            {"created_at": now, "name": "경기"},
            {"created_at": now, "name": "강원"},
            {"created_at": now, "name": "충북"},
            {"created_at": now, "name": "충남"},
            {"created_at": now, "name": "경북"},
            {"created_at": now, "name": "경남"},
            {"created_at": now, "name": "전북"},
            {"created_at": now, "name": "전남"},
        ],
    )

    # positions
    op.bulk_insert(
        sa.table(
            "positions",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "보컬"},
            {"created_at": now, "name": "일렉 기타"},
            {"created_at": now, "name": "어쿠스틱 기타"},
            {"created_at": now, "name": "베이스"},
            {"created_at": now, "name": "드럼"},
            {"created_at": now, "name": "키보드"},
        ],
    )

    # genres
    op.bulk_insert(
        sa.table(
            "genres",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "인디락"},
            {"created_at": now, "name": "K-pop"},
            {"created_at": now, "name": "J-pop"},
            {"created_at": now, "name": "메탈"},
            {"created_at": now, "name": "하드락"},
            {"created_at": now, "name": "재즈"},
        ],
    )

    # experience_levels
    op.bulk_insert(
        sa.table(
            "experience_levels",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "취미 1년 이하"},
            {"created_at": now, "name": "취미 3년 이하"},
            {"created_at": now, "name": "취미 5년 이하"},
            {"created_at": now, "name": "취미 5년 이상"},
            {"created_at": now, "name": "전공"},
            {"created_at": now, "name": "프로"},
        ],
    )

    # orientations
    op.bulk_insert(
        sa.table(
            "orientations",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "취미"},
            {"created_at": now, "name": "프로"},
            {"created_at": now, "name": "프로 지향"},
        ],
    )

    # recruitment_types
    op.bulk_insert(
        sa.table(
            "recruitment_types",
            sa.column("created_at", sa.DateTime()),
            sa.column("name", sa.String(length=50)),
        ),
        [
            {"created_at": now, "name": "고정 밴드"},
            {"created_at": now, "name": "프로젝트 밴드"},
        ],
    )
    # ### end Alembic commands ###


def downgrade():
    """Downgrade schema."""
    op.execute("DELETE FROM regions")
    op.execute("DELETE FROM positions")
    op.execute("DELETE FROM genres")
    op.execute("DELETE FROM experience_levels")
    op.execute("DELETE FROM orientations")
    op.execute("DELETE FROM recruitment_types")
    # ### end Alembic commands ###
