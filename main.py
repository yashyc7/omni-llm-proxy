import sys
import uvicorn
from app.api.server import app
from app.core.config import DEFAULT_PROVIDER, PORT

if __name__ == "__main__":
    app.state.provider_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROVIDER
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=False)
