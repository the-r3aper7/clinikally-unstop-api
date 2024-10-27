from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import json
from pathlib import Path
from math import ceil

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Data Models
class Product(BaseModel):
    product_id: int
    product_name: str
    price: float
    in_stock: bool
    product_image: str

class PincodeInfo(BaseModel):
    pincode: int
    logistics_provider: str
    delivery_tat_days: int

class PaginatedResponse(BaseModel):
    items: List[Product]
    total: int
    page: int
    total_pages: int
    has_next: bool
    has_prev: bool

# Load data from JSON file
def load_data():
    try:
        with open('data_with_images.json', 'r') as file:
            data = json.load(file)
            return {
                'products': [Product(**product) for product in data['products']],
                'pincode_data': [PincodeInfo(**pincode) for pincode in data['delivery_info']['pincode_data']]
            }
    except Exception as e:
        # For Vercel, we'll include sample data directly
        return {
            'products': [
                Product(
                    product_id=1,
                    product_name="Product 1",
                    price=63.54,
                    in_stock=True
                ),
                # Add more sample products
            ],
            'pincode_data': [
                PincodeInfo(
                    pincode=117485,
                    logistics_provider="General Partners",
                    delivery_tat_days=4
                ),
                # Add more sample pincode data
            ]
        }

# Initialize data
data_store = load_data()

@app.get("/api/products", response_model=PaginatedResponse)
async def get_products(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    in_stock: Optional[bool] = None
):
    filtered_products = data_store['products']
    if in_stock is not None:
        filtered_products = [p for p in filtered_products if p.in_stock == in_stock]
    
    total_items = len(filtered_products)
    total_pages = ceil(total_items / limit)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_items = filtered_products[start_idx:end_idx]
    
    return PaginatedResponse(
        items=paginated_items,
        total=total_items,
        page=page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product_details(product_id: int):
    product = next(
        (p for p in data_store['products'] if p.product_id == product_id),
        None
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/pincode/{pincode}", response_model=PincodeInfo)
async def get_pincode_details(pincode: int):
    pincode_info = next(
        (p for p in data_store['pincode_data'] if p.pincode == pincode),
        None
    )
    if not pincode_info:
        raise HTTPException(status_code=404, detail="Pincode not found")
    return pincode_info


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the index.html file"""
    try:
        with open("templates/index.html") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Return a default HTML if index.html doesn't exist
        return """
        <html>
            <head>
                <title>FastAPI HTML Server</title>
            </head>
            <body>
                <h1>Welcome to FastAPI HTML Server</h1>
                <p>Place your HTML files in the templates directory to serve them.</p>
            </body>
        </html>
        """

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy"}