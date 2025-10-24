from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry


app = FastAPI(title="Doctor Onboarding API")

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Doctor Onboarding API!"

temp_schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(temp_schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {
        "message": "Doctor Onboarding API",
        "graphql": "/graphql",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}