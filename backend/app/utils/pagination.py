from sqlalchemy import or_


def apply_pagination(query, page: int, page_size: int):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = query.count()
    return query.offset((page - 1) * page_size).limit(page_size).all(), total, page, page_size


def text_search(query, model, term: str | None, fields: list[str]):
    if not term:
        return query
    like = f"%{term}%"
    return query.filter(or_(*[getattr(model, field).ilike(like) for field in fields]))
