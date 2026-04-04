from app.routes.auth import router as auth_router
from app.routes.nc_upload import router as nc_upload_router
from app.routes.outlet import router as outlet_router
from app.routes.sales_upload import router as sales_upload_router

__all__ = ["auth_router", "nc_upload_router", "outlet_router", "sales_upload_router"]
