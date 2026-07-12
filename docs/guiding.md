1. Condition
I'm on an internship project with flyrank AI. The project go through 10 weeks and every week have some tasks to be done. The tasks I will write it in phase 3. You follow the tasks and create the plan of what need to be done step by step so I can easily review quick. Create plan as simple, short, straight forward as possible, don't need details if I dont ask for.

2. Tech stacks: FastAPI, Docker, Postgres, Python. Follow clean architecture for project structure (create project structure/skeleton first). Always create decoupled code and follow SOLID, DRY principles.

3. Flyrank demand
Goal
Run Postgres in Docker, connect your A2 service to it (swapping the in-memory store for a real repository), and start app + database together with one command.

Purpose
This is the survival kit applied in one real task: Docker, SQL, .env, and the payoff of A2's layering — proving that "switch storage" really does change only one file. Data that survives a restart is the moment your project stops being a demo. Every later week (jobs, caching, RAG) assumes this local stack.

The task
Start Postgres in Docker with a volume so data persists (the Docker guide has the exact command).
Put the connection string in .env — gitignored, with a committed .env.example .
Create your table with one SQL file (or a tiny init script)
Write a Postgres repository implementing the same interface as your in-memory one, and swap it in. Your service and routes must not change — that's the architecture proving itself.
docker-compose.yml : app + database together; docker compose up runs the whole stack.
Prove persistence: create rows → restart app and container → rows still there.
Requirements
Postgres runs in Docker with a volume ; the whole stack starts with docker compose up .
Connection string from .env (gitignored; .env.example committed).
A Postgres repository replaced the in-memory one — service and routes unchanged (say so in the README, honestly).
Persistence proven across an app + container restart (how you checked goes in the README).
Stretch (optional)
Add Redis to the compose file (you'll want it in W4) and ping it from the app.
Add one index and show EXPLAIN ANALYZE before/after on a seeded table.