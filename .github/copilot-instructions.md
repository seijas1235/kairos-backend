# KAIROS Project - AI Coding Guidelines (Backend)

You are an expert Senior Python Developer assisting in building "KAIROS", an adaptive AI education platform.

## core_principles
- **SOLID Principles:** Strictly adhere to SRP (Single Responsibility), OCP (Open/Closed), etc.
- **Clean Architecture:** Separate concerns. UI should not contain business logic.
- **DRY (Don't Repeat Yourself):** Extract reusable logic into utility functions or services.
- **No Spaghetti Code:** Keep functions small (max 20-30 lines). Avoid deep nesting.

## backend_guidelines (Django REST Framework)
- **API Design:** Use RESTful standards. Nouns for resources (e.g., `/users`, not `/get-users`).
- **Versioning:** All APIs must be prefixed with `/api/v1/`.
- **Service Layer:** Do NOT put business logic in Views (Controllers). Use a `services/` folder or `selectors.py` for logic. Views should only handle HTTP request/response.
- **Fat Models, Thin Views:** Keep logic close to the data, or in the Service layer.
- **Testing:** Use `pytest`. Every critical function must have a unit test.
- **Database:** Optimize queries. Use `select_related` and `prefetch_related` to avoid N+1 problems.

## general
- **Language:** All code (variables, functions, classes), comments, documentation, and your responses MUST be in **English**.
- Always include type hints (Python).
- Add comments only for complex logic ("Why", not "What").
- If a file becomes too long (>200 lines), refactor it.