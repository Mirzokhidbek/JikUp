from collections.abc import Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Skill
from app.nlp.skills import SkillEntry, load_dictionary


async def sync_skills(
    session: AsyncSession, entries: Sequence[SkillEntry] | None = None
) -> dict[str, int]:
    rows = [
        {"canonical_name": e.name, "category": e.category, "aliases": list(e.aliases)}
        for e in (entries if entries is not None else load_dictionary())
    ]
    base = insert(Skill).values(rows)
    stmt = base.on_conflict_do_update(
        index_elements=[Skill.canonical_name],
        set_={"category": base.excluded.category, "aliases": base.excluded.aliases},
    ).returning(Skill.id, Skill.canonical_name)
    result = await session.execute(stmt)
    return {name: skill_id for skill_id, name in result.all()}
