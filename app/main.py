from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app.schema import schema
from app.database import db

app = FastAPI(
    title="Doctor Onboarding API",
    description="GraphQL API for doctor onboarding process",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
async def startup():
    """Connect to database on startup"""
    db.connect()
    print("✅ Database connected successfully")

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    db.close()
    print("🔌 Database connection closed")

@app.get("/")
def root():
    return {
        "message": "Doctor Onboarding API",
        "version": "1.0.0",
        "endpoints": {
            "graphql": "/graphql",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = db.execute_one("SELECT 1 as status")
        return {
            "status": "healthy",
            "database": "connected" if result else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }