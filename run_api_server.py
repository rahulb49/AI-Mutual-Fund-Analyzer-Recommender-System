"""
API Startup Script
Simple script to start the FastAPI server
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    import uvicorn
    from api.main import app
    
    print("="*70)
    print("Starting NAV Analysis API Server")
    print("="*70)
    print("\n📚 Interactive API Documentation:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n🔗 API Base URL: http://localhost:8000")
    print("\n📝 Example Endpoints:")
    print("   GET  /health                          - Health check")
    print("   GET  /api/schemes                      - List schemes")
    print("   GET  /api/schemes/search?query=ICICI - Search schemes")
    print("   GET  /api/schemes/{code}              - Scheme analysis")
    print("   GET  /api/compare?scheme_codes=1,2,3 - Compare schemes")
    print("   GET  /api/top-schemes?metric=sharpe_ratio - Top schemes")
    print("   GET  /api/statistics                   - Market statistics")
    print("\n✓ Starting server... (Press Ctrl+C to stop)")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
