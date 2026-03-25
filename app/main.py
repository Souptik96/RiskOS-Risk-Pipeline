from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pipeline import RiskPipeline
from schemas import PipelineRequest, PipelineResponse
import uvicorn
import time

app = FastAPI(
    title="RiskOS Risk Pipeline API",
    description="Automated transaction triage engine combining ML scoring and rule-based decision-making",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RiskPipeline()

@app.post("/api/v1/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest):
    """Run risk pipeline on a batch of transactions"""
    start_time = time.time()
    
    try:
        result = pipeline.process_batch(request.transactions)
        latency_ms = (time.time() - start_time) * 1000
        
        return PipelineResponse(
            batch_id=request.batch_id,
            total_transactions=len(request.transactions),
            auto_approved=result["auto_approved"],
            manual_review=result["manual_review"],
            auto_rejected=result["auto_rejected"],
            workload_reduction_percent=result["workload_reduction_percent"],
            processing_time_ms=round(latency_ms, 2),
            results=result["results"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)