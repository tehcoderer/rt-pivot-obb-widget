#!/usr/bin/env python3
"""
Portfolio Analytics Widget for OpenBB
Real-time portfolio analytics with 35,000 positions and 200+ metrics
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from functools import wraps
import uvicorn
import logging
from typing import Dict, List, Any, Set
from fastapi.websockets import WebSocketState
from datetime import datetime
import numpy as np
import threading
import time
import pandas as pd
from data_generator import portfolio_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIDGETS = {}

def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

app = FastAPI(
    title="Portfolio Analytics Widget",
    description="Real-time portfolio analytics for OpenBB Workspace with 35,000+ positions",
    version="1.0.0"
)

origins = [
    "https://pro.openbb.co",
    "http://localhost:3000",  # For local development
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "service": "Portfolio Analytics Widget",
        "version": "1.0.0",
        "description": "Real-time portfolio analytics with 35,000+ positions and 200+ metrics",
        "endpoints": {
            "widgets": "/widgets.json",
            "portfolio_analytics": "/portfolio_analytics",
            "portfolio_tree": "/portfolio_tree", 
            "portfolio_pivot": "/portfolio_pivot",
            "real_time_updates": "/real_time_updates"
        }
    }

@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets"""
    return WIDGETS

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

# Portfolio Analytics Widgets

@register_widget({
    "name": "Portfolio Analytics - Flat View",
    "description": "Real-time portfolio analytics with 35,000+ positions and 200+ metrics",
    "type": "table",
    "endpoint": "portfolio_analytics",
    "gridData": {"w": 24, "h": 16},
    "staleTime": 30000,  # 30 seconds
    "refetchInterval": 5000,  # 5 seconds for real-time updates
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": True,
            "defaultColDef": {
                "resizable": True,
                "sortable": True,
                "filter": True,
                "floatingFilter": True,
                "enablePivot": True,
                "enableRowGroup": True,
                "enableValue": True
            },
            "columnsDefs": [
                # Identifiers
                {
                    "field": "Fund",
                    "headerName": "Fund",
                    "pinned": "left",
                    "width": 100,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Strategy", 
                    "headerName": "Strategy",
                    "pinned": "left",
                    "width": 120,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "PM",
                    "headerName": "PM",
                    "pinned": "left", 
                    "width": 100,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Portfolio",
                    "headerName": "Portfolio",
                    "pinned": "left",
                    "width": 120,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Ticker",
                    "headerName": "Ticker",
                    "pinned": "left",
                    "width": 80,
                    "cellDataType": "text"
                },
                {
                    "field": "Quantity",
                    "headerName": "Quantity", 
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum"
                },
                {
                    "field": "Price",
                    "headerName": "Price",
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed"
                },
                {
                    "field": "MarketValue",
                    "headerName": "Market Value",
                    "width": 120,
                    "cellDataType": "number", 
                    "formatterFn": "int",
                    "aggFunc": "sum",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 5000000, "color": "#22c55e", "fill": False},
                            {"condition": "lt", "value": 1000000, "color": "#f59e0b", "fill": False}
                        ]
                    }
                },
                {
                    "field": "PnL_Day",
                    "headerName": "P&L Day",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int", 
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "PnL_MTD", 
                    "headerName": "P&L MTD",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "VaR_95",
                    "headerName": "VaR 95%",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum"
                },
                {
                    "field": "Beta",
                    "headerName": "Beta",
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "none"
                },
                {
                    "field": "ADV%",
                    "headerName": "ADV%", 
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "percent"
                },
                {
                    "field": "LiquidityFlag",
                    "headerName": "Liquidity",
                    "width": 100,
                    "cellDataType": "text",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "OK", "color": "#22c55e", "fill": True},
                            {"condition": "eq", "value": "Watch", "color": "#f59e0b", "fill": True},
                            {"condition": "eq", "value": "Restricted", "color": "#ef4444", "fill": True},
                            {"condition": "eq", "value": "Blocked", "color": "#dc2626", "fill": True}
                        ]
                    }
                },
                {
                    "field": "Sector",
                    "headerName": "Sector",
                    "width": 120,
                    "cellDataType": "text",
                    "enablePivot": True
                },
                {
                    "field": "Region",
                    "headerName": "Region", 
                    "width": 120,
                    "cellDataType": "text",
                    "enablePivot": True
                }
            ]
        }
    }
})
@app.get("/portfolio_analytics")
def portfolio_analytics():
    """Returns real-time portfolio analytics data"""
    try:
        # Get or generate data
        data = portfolio_generator.get_current_data()
        if data is None:
            logger.info("Generating initial portfolio data...")
            data = portfolio_generator.generate_portfolio_data(35000)
            portfolio_generator.set_current_data(data)
            portfolio_generator.start_real_time_updates()
        
        # Return as list of dictionaries for AGGrid
        return data.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error in portfolio_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@register_widget({
    "name": "Full Portfolio Analytics",
    "description": "Configurable portfolio analytics with user-selectable aggregation and filtering",
    "type": "table",
    "endpoint": "full_portfolio_analytics",
    "gridData": {"w": 24, "h": 16},
    "staleTime": 30000,
    "refetchInterval": 5000,
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": True,
            "defaultColDef": {
                "resizable": True,
                "sortable": True,
                "filter": True,
                "floatingFilter": True,
                "enablePivot": True,
                "enableRowGroup": True,
                "enableValue": True
            },
            "columnsDefs": [
                # Identifiers
                {
                    "field": "Fund",
                    "headerName": "Fund",
                    "pinned": "left",
                    "width": 100,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Strategy", 
                    "headerName": "Strategy",
                    "pinned": "left",
                    "width": 120,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "PM",
                    "headerName": "PM",
                    "pinned": "left", 
                    "width": 100,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Portfolio",
                    "headerName": "Portfolio",
                    "pinned": "left",
                    "width": 120,
                    "rowGroup": True,
                    "hide": True
                },
                {
                    "field": "Ticker",
                    "headerName": "Ticker",
                    "pinned": "left",
                    "width": 80,
                    "cellDataType": "text"
                },
                {
                    "field": "Quantity",
                    "headerName": "Quantity", 
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum"
                },
                {
                    "field": "Price",
                    "headerName": "Price",
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed"
                },
                {
                    "field": "MarketValue",
                    "headerName": "Market Value",
                    "width": 120,
                    "cellDataType": "number", 
                    "formatterFn": "int",
                    "aggFunc": "sum",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 5000000, "color": "#22c55e", "fill": False},
                            {"condition": "lt", "value": 1000000, "color": "#f59e0b", "fill": False}
                        ]
                    }
                },
                {
                    "field": "PnL_Day",
                    "headerName": "P&L Day",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int", 
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "PnL_MTD", 
                    "headerName": "P&L MTD",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "VaR_95",
                    "headerName": "VaR 95%",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum"
                },
                {
                    "field": "Beta",
                    "headerName": "Beta",
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "none"
                },
                {
                    "field": "ADV%",
                    "headerName": "ADV%", 
                    "width": 80,
                    "cellDataType": "number",
                    "formatterFn": "percent"
                },
                {
                    "field": "LiquidityFlag",
                    "headerName": "Liquidity",
                    "width": 100,
                    "cellDataType": "text",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "OK", "color": "#22c55e", "fill": True},
                            {"condition": "eq", "value": "Watch", "color": "#f59e0b", "fill": True},
                            {"condition": "eq", "value": "Restricted", "color": "#ef4444", "fill": True},
                            {"condition": "eq", "value": "Blocked", "color": "#dc2626", "fill": True}
                        ]
                    }
                },
                {
                    "field": "Sector",
                    "headerName": "Sector",
                    "width": 120,
                    "cellDataType": "text",
                    "enablePivot": True
                },
                {
                    "field": "Region",
                    "headerName": "Region", 
                    "width": 120,
                    "cellDataType": "text",
                    "enablePivot": True
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "viewMode",
            "type": "text",
            "label": "View Mode",
            "description": "Select the analysis view mode",
            "value": "summary",
            "show": True,
            "options": [
                {"label": "Summary View (Fund Level)", "value": "summary"},
                {"label": "Portfolio Manager View", "value": "pm"},
                {"label": "Detailed Position View", "value": "detailed"},
                {"label": "Custom Grouping", "value": "custom"}
            ]
        },
        {
            "paramName": "groupBy",
            "type": "text",
            "label": "Group By",
            "description": "Select primary grouping level (only when Custom Grouping is selected)",
            "value": "Fund",
            "show": True,
            "options": [
                {"label": "Fund", "value": "Fund"},
                {"label": "Strategy", "value": "Strategy"},
                {"label": "Portfolio Manager", "value": "PM"},
                {"label": "Portfolio", "value": "Portfolio"},
                {"label": "Sector", "value": "Sector"},
                {"label": "Region", "value": "Region"},
                {"label": "Liquidity Flag", "value": "LiquidityFlag"}
            ]
        },
        {
            "paramName": "secondaryGroup",
            "type": "text",
            "label": "Secondary Group",
            "description": "Optional secondary grouping level",
            "value": "none",
            "show": True,
            "options": [
                {"label": "No Secondary Grouping", "value": "none"},
                {"label": "Fund", "value": "Fund"},
                {"label": "Strategy", "value": "Strategy"},
                {"label": "Portfolio Manager", "value": "PM"},
                {"label": "Portfolio", "value": "Portfolio"},
                {"label": "Sector", "value": "Sector"},
                {"label": "Region", "value": "Region"},
                {"label": "Liquidity Flag", "value": "LiquidityFlag"}
            ]
        },
        {
            "paramName": "filterFund",
            "type": "text",
            "label": "Filter by Fund",
            "description": "Filter positions by specific fund",
            "value": "all",
            "show": True,
            "options": [
                {"label": "All Funds", "value": "all"},
                {"label": "Global Equity", "value": "GlobalEq"},
                {"label": "Fixed Income", "value": "FixedIncome"},
                {"label": "Alternatives", "value": "Alternatives"},
                {"label": "Emerging Markets", "value": "EmergingMkt"},
                {"label": "Small Cap", "value": "SmallCap"}
            ]
        },
        {
            "paramName": "filterPM",
            "type": "text",
            "label": "Filter by PM",
            "description": "Filter positions by portfolio manager",
            "value": "all",
            "show": True,
            "options": [
                {"label": "All PMs", "value": "all"},
                {"label": "Jane Doe", "value": "Jane Doe"},
                {"label": "John Smith", "value": "John Smith"},
                {"label": "Alice Johnson", "value": "Alice Johnson"},
                {"label": "Bob Wilson", "value": "Bob Wilson"},
                {"label": "Carol Brown", "value": "Carol Brown"}
            ]
        },
        {
            "paramName": "minMarketValue",
            "type": "number",
            "label": "Min Market Value",
            "description": "Minimum market value filter (USD)",
            "value": 0,
            "show": True
        },
        {
            "paramName": "maxPositions",
            "type": "number",
            "label": "Max Positions",
            "description": "Maximum number of positions to display",
            "value": 1000,
            "show": True
        },
        {
            "paramName": "showDetails",
            "type": "boolean",
            "label": "Show Position Details",
            "description": "Show individual positions or only aggregated data",
            "value": True,
            "show": True
        }
    ]
})
@app.get("/full_portfolio_analytics")
def full_portfolio_analytics(
    viewMode: str = "summary",
    groupBy: str = "Fund",
    secondaryGroup: str = "none", 
    filterFund: str = "all",
    filterPM: str = "all",
    minMarketValue: float = 0,
    maxPositions: int = 1000,
    showDetails: bool = True
):
    """Returns configurable portfolio analytics with user-defined aggregation and filtering"""
    try:
        # Get or generate data
        data = portfolio_generator.get_current_data()
        if data is None:
            logger.info("Generating initial portfolio data...")
            data = portfolio_generator.generate_portfolio_data(35000)
            portfolio_generator.set_current_data(data)
            portfolio_generator.start_real_time_updates()
        
        # Apply filters
        filtered_data = data.copy()
        
        # Fund filter
        if filterFund != "all":
            filtered_data = filtered_data[filtered_data['Fund'] == filterFund]
        
        # PM filter
        if filterPM != "all":
            filtered_data = filtered_data[filtered_data['PM'] == filterPM]
        
        # Market value filter
        if minMarketValue > 0:
            filtered_data = filtered_data[filtered_data['MarketValue'] >= minMarketValue]
        
        # Determine grouping based on view mode
        if viewMode == "summary":
            group_cols = ["Fund"]
            showDetails = False  # Override to show only summary
        elif viewMode == "pm":
            group_cols = ["PM"]
            showDetails = False  # Override to show only summary
        elif viewMode == "detailed":
            group_cols = []  # No grouping for detailed view
        elif viewMode == "custom":
            group_cols = [groupBy] if groupBy != "none" else []
            if secondaryGroup != "none" and secondaryGroup != groupBy:
                group_cols.append(secondaryGroup)
        else:
            group_cols = []
        
        # Apply grouping if specified
        if len(group_cols) > 0:
            
            # Aggregate data
            agg_funcs = {
                'MarketValue': 'sum',
                'PnL_Day': 'sum',
                'PnL_MTD': 'sum',
                'PnL_QTD': 'sum',
                'PnL_YTD': 'sum',
                'VaR_95': 'sum',
                'VaR_99': 'sum',
                'Quantity': 'sum',
                'Ticker': 'count'  # Position count
            }
            
            grouped_data = filtered_data.groupby(group_cols).agg(agg_funcs).reset_index()
            grouped_data = grouped_data.rename(columns={'Ticker': 'PositionCount'})
            
            # Add computed metrics
            grouped_data['AvgBeta'] = filtered_data.groupby(group_cols)['Beta'].mean().values
            grouped_data['AvgADV'] = filtered_data.groupby(group_cols)['ADV%'].mean().values
            
            # If not showing details, return aggregated data only
            if not showDetails:
                result_data = grouped_data
            else:
                # Combine aggregated and detailed data
                # Add a grouping indicator to detailed data
                detailed_data = filtered_data.copy()
                detailed_data['DataType'] = 'Position'
                grouped_data['DataType'] = 'Summary'
                
                # Efficiently align columns using pandas operations
                # Find common columns and fill missing ones
                common_cols = set(detailed_data.columns) & set(grouped_data.columns)
                detailed_only_cols = set(detailed_data.columns) - set(grouped_data.columns)
                grouped_only_cols = set(grouped_data.columns) - set(detailed_data.columns)
                
                # Add missing columns efficiently
                for col in detailed_only_cols:
                    grouped_data[col] = None
                for col in grouped_only_cols:
                    detailed_data[col] = None
                
                # Combine data
                result_data = pd.concat([grouped_data, detailed_data], ignore_index=True)
        else:
            result_data = filtered_data
        
        # Limit number of positions
        if len(result_data) > maxPositions:
            # Sort by market value descending and take top positions
            result_data = result_data.nlargest(maxPositions, 'MarketValue')
        
        # Clean data for JSON serialization (handle NaN, infinity values)
        result_data = result_data.fillna(0)  # Replace NaN with 0
        result_data = result_data.replace([float('inf'), float('-inf')], [999999999, -999999999])  # Replace infinity
        
        # Return as list of dictionaries for AGGrid
        return result_data.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error in full_portfolio_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@register_widget({
    "name": "Portfolio Analytics - Tree View",
    "description": "Hierarchical portfolio view with Fund > Strategy > PM > Portfolio drill-down",
    "type": "table", 
    "endpoint": "portfolio_tree",
    "gridData": {"w": 24, "h": 16},
    "staleTime": 30000,
    "refetchInterval": 5000,
    "data": {
        "table": {
            "enableCharts": True,
            "treeData": True,
            "autoGroupColumnDef": {
                "headerName": "Portfolio Hierarchy",
                "field": "Fund",
                "cellRenderer": "agGroupCellRenderer",
                "cellRendererParams": {
                    "suppressCount": False,
                    "suppressDoubleClickExpand": False
                },
                "pinned": "left",
                "width": 300
            },
            "getDataPath": "(data) => data.path",
            "groupDefaultExpanded": 1,
            "columnsDefs": [
                {
                    "field": "MarketValue",
                    "headerName": "Market Value", 
                    "width": 140,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum",
                    "renderFn": "columnColor"
                },
                {
                    "field": "PnL_Day",
                    "headerName": "P&L Day",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "PnL_MTD",
                    "headerName": "P&L MTD", 
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed",
                    "aggFunc": "sum"
                },
                {
                    "field": "VaR_95",
                    "headerName": "VaR 95%",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "aggFunc": "sum"
                },
                {
                    "field": "PositionCount",
                    "headerName": "Positions",
                    "width": 100,
                    "cellDataType": "number",
                    "aggFunc": "sum"
                }
            ]
        }
    }
})
@app.get("/portfolio_tree")
def portfolio_tree():
    """Returns hierarchical portfolio data for tree view"""
    try:
        data = portfolio_generator.get_current_data()
        if data is None:
            data = portfolio_generator.generate_portfolio_data(35000)
            portfolio_generator.set_current_data(data)
            portfolio_generator.start_real_time_updates()
        
        # Create hierarchical structure
        tree_data = []
        
        # Group by hierarchy levels
        grouped = data.groupby(['Fund', 'Strategy', 'PM', 'Portfolio']).agg({
            'MarketValue': 'sum',
            'PnL_Day': 'sum', 
            'PnL_MTD': 'sum',
            'VaR_95': 'sum',
            'Ticker': 'count'
        }).rename(columns={'Ticker': 'PositionCount'}).reset_index()
        
        for _, row in grouped.iterrows():
            # Create path for tree structure
            path = [row['Fund'], row['Strategy'], row['PM'], row['Portfolio']]
            
            tree_data.append({
                'path': path,
                'Fund': row['Fund'],
                'Strategy': row['Strategy'], 
                'PM': row['PM'],
                'Portfolio': row['Portfolio'],
                'MarketValue': row['MarketValue'],
                'PnL_Day': row['PnL_Day'],
                'PnL_MTD': row['PnL_MTD'],
                'VaR_95': row['VaR_95'],
                'PositionCount': row['PositionCount']
            })
        
        return tree_data
        
    except Exception as e:
        logger.error(f"Error in portfolio_tree: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@register_widget({
    "name": "Portfolio Analytics - Pivot View",
    "description": "Pivot table view for slicing and dicing portfolio data",
    "type": "table",
    "endpoint": "portfolio_pivot", 
    "gridData": {"w": 24, "h": 16},
    "staleTime": 30000,
    "refetchInterval": 5000,
    "data": {
        "table": {
            "enableCharts": True,
            "pivotMode": True,
            "sideBar": {
                "toolPanels": [
                    {
                        "id": "columns",
                        "labelDefault": "Columns",
                        "labelKey": "columns",
                        "iconKey": "columns",
                        "toolPanel": "agColumnsToolPanel"
                    },
                    {
                        "id": "filters", 
                        "labelDefault": "Filters",
                        "labelKey": "filters",
                        "iconKey": "filter",
                        "toolPanel": "agFiltersToolPanel"
                    }
                ]
            },
            "columnsDefs": [
                # Dimensions
                {
                    "field": "Fund",
                    "headerName": "Fund",
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                {
                    "field": "Strategy",
                    "headerName": "Strategy", 
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                {
                    "field": "PM",
                    "headerName": "PM",
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                {
                    "field": "Sector",
                    "headerName": "Sector",
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                {
                    "field": "Region",
                    "headerName": "Region",
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                {
                    "field": "LiquidityFlag",
                    "headerName": "Liquidity",
                    "enablePivot": True,
                    "enableRowGroup": True
                },
                # Measures
                {
                    "field": "MarketValue",
                    "headerName": "Market Value",
                    "enableValue": True,
                    "aggFunc": "sum",
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "PnL_Day",
                    "headerName": "P&L Day",
                    "enableValue": True,
                    "aggFunc": "sum",
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "PnL_MTD",
                    "headerName": "P&L MTD",
                    "enableValue": True,
                    "aggFunc": "sum", 
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "VaR_95",
                    "headerName": "VaR 95%",
                    "enableValue": True,
                    "aggFunc": "sum",
                    "cellDataType": "number", 
                    "formatterFn": "int"
                }
            ]
        }
    }
})
@app.get("/portfolio_pivot")
def portfolio_pivot():
    """Returns portfolio data optimized for pivot analysis"""
    try:
        data = portfolio_generator.get_current_data()
        if data is None:
            data = portfolio_generator.generate_portfolio_data(35000)
            portfolio_generator.set_current_data(data)
            portfolio_generator.start_real_time_updates()
        
        # Return subset of columns relevant for pivoting
        pivot_columns = [
            'Fund', 'Strategy', 'PM', 'Portfolio', 'Ticker',
            'Sector', 'Region', 'Currency', 'LiquidityFlag',
            'MarketValue', 'PnL_Day', 'PnL_MTD', 'PnL_QTD', 'PnL_YTD',
            'VaR_95', 'VaR_99', 'Beta', 'Volatility', 'ADV%'
        ]
        
        return data[pivot_columns].to_dict('records')
        
    except Exception as e:
        logger.error(f"Error in portfolio_pivot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/real_time_updates")
def real_time_updates():
    """Endpoint for real-time data updates"""
    try:
        data = portfolio_generator.get_current_data()
        if data is None:
            return {"message": "No data available"}
        
        return {
            "timestamp": time.time(),
            "total_positions": len(data),
            "total_market_value": data['MarketValue'].sum(),
            "total_pnl_day": data['PnL_Day'].sum(),
            "total_pnl_mtd": data['PnL_MTD'].sum(),
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        logger.error(f"Error in real_time_updates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LIVE GRID WIDGET WITH WEBSOCKET ====================

# Sample data store for live grid
LIVE_WS_DATA = {}

def get_live_position_data(symbols: List[str]):
    """Generate real-time position data for specified symbols"""
    data = portfolio_generator.get_current_data()
    if data is None or len(data) == 0:
        data = portfolio_generator.generate_portfolio_data(1000)  # Smaller dataset for live updates
        portfolio_generator.set_current_data(data)
    
    # Filter data to requested symbols if any, otherwise get top positions
    if symbols and len(symbols) > 0:
        filtered_data = data[data['Ticker'].isin(symbols)]
    else:
        # Get top 20 positions by market value for live demo
        filtered_data = data.nlargest(20, 'MarketValue')
    
    # Add some random price movement simulation
    for idx in filtered_data.index:
        symbol = filtered_data.loc[idx, 'Ticker']
        current_price = filtered_data.loc[idx, 'Price']
        
        # Store initial price if not exists
        if symbol not in LIVE_WS_DATA:
            LIVE_WS_DATA[symbol] = {
                'initial_price': current_price,
                'prev_price': current_price
            }
        
        # Simulate price movement
        prev_price = LIVE_WS_DATA[symbol]['prev_price']
        price_change = np.random.uniform(-0.05, 0.05)  # ±5% movement
        new_price = prev_price * (1 + price_change)
        
        # Update stored data
        LIVE_WS_DATA[symbol]['prev_price'] = new_price
        
        # Calculate changes
        day_change = new_price - LIVE_WS_DATA[symbol]['initial_price']
        day_change_percent = (day_change / LIVE_WS_DATA[symbol]['initial_price']) * 100
        
        # Update the dataframe
        data.loc[idx, 'Price'] = new_price
        data.loc[idx, 'PnL_Day'] = day_change * filtered_data.loc[idx, 'Quantity']
        data.loc[idx, 'MarketValue'] = new_price * filtered_data.loc[idx, 'Quantity']
    
    return filtered_data

@register_widget({
    "name": "Live Portfolio Grid",
    "description": "Real-time portfolio positions with WebSocket live updates",
    "type": "live_grid",
    "endpoint": "live_portfolio_positions",
    "wsEndpoint": "ws",
    "gridData": {"w": 24, "h": 12},
    "data": {
        "wsRowIdColumn": "Ticker",
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "Ticker",
                    "headerName": "Symbol",
                    "width": 80,
                    "pinned": "left"
                },
                {
                    "field": "Fund",
                    "headerName": "Fund", 
                    "width": 100,
                    "enableCellChangeWs": False
                },
                {
                    "field": "Strategy",
                    "headerName": "Strategy",
                    "width": 120,
                    "enableCellChangeWs": False
                },
                {
                    "field": "Price",
                    "headerName": "Price",
                    "width": 90,
                    "renderFn": "showCellChange",
                    "renderFnParams": {
                        "colorValueKey": "PnL_Day"
                    },
                    "formatterFn": "int"
                },
                {
                    "field": "Quantity",
                    "headerName": "Quantity",
                    "width": 100,
                    "formatterFn": "int",
                    "enableCellChangeWs": False
                },
                {
                    "field": "MarketValue",
                    "headerName": "Market Value",
                    "width": 120,
                    "renderFn": "showCellChange",
                    "renderFnParams": {
                        "colorValueKey": "PnL_Day"
                    },
                    "formatterFn": "int"
                },
                {
                    "field": "PnL_Day",
                    "headerName": "P&L Day",
                    "width": 100,
                    "renderFn": "greenRed",
                    "formatterFn": "int"
                },
                {
                    "field": "VaR_95",
                    "headerName": "VaR 95%",
                    "width": 90,
                    "formatterFn": "int",
                    "enableCellChangeWs": False
                },
                {
                    "field": "Beta",
                    "headerName": "Beta",
                    "width": 70,
                    "formatterFn": "none",
                    "enableCellChangeWs": False
                },
                {
                    "field": "LiquidityFlag",
                    "headerName": "Liquidity",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "OK", "color": "#22c55e", "fill": True},
                            {"condition": "eq", "value": "Watch", "color": "#f59e0b", "fill": True},
                            {"condition": "eq", "value": "Restricted", "color": "#ef4444", "fill": True}
                        ]
                    },
                    "enableCellChangeWs": False
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "symbols",
            "description": "Comma-separated list of symbols to track",
            "value": "AAPL,GOOGL,MSFT,AMZN,TSLA",
            "label": "Symbols",
            "type": "text",
            "multiSelect": True,
            "options": [
                {"label": "AAPL", "value": "AAPL"},
                {"label": "GOOGL", "value": "GOOGL"},
                {"label": "MSFT", "value": "MSFT"},
                {"label": "AMZN", "value": "AMZN"},
                {"label": "TSLA", "value": "TSLA"},
                {"label": "NVDA", "value": "NVDA"},
                {"label": "META", "value": "META"},
                {"label": "JPM", "value": "JPM"},
                {"label": "V", "value": "V"},
                {"label": "JNJ", "value": "JNJ"}
            ]
        }
    ]
})
@app.get("/live_portfolio_positions")
def live_portfolio_positions(symbols: str = "AAPL,GOOGL,MSFT,AMZN,TSLA"):
    """Initial data endpoint for live grid"""
    try:
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        data = get_live_position_data(symbol_list)
        
        # Add date for compatibility
        result = []
        for _, row in data.iterrows():
            row_dict = row.to_dict()
            row_dict['date'] = datetime.now().date().isoformat()
            result.append(row_dict)
        
        # Clean data for JSON serialization
        for item in result:
            for key, value in item.items():
                if pd.isna(value) or value == float('inf') or value == float('-inf'):
                    item[key] = 0
        
        return result
        
    except Exception as e:
        logger.error(f"Error in live_portfolio_positions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for live updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live portfolio updates"""
    await websocket.accept()
    try:
        await websocket_handler(websocket)
    except WebSocketDisconnect:
        return
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011)

async def websocket_handler(websocket: WebSocket):
    """Handle WebSocket connections for live portfolio updates"""
    subscribed_symbols: Set[str] = set()

    async def consumer_handler(ws: WebSocket):
        """Handle incoming WebSocket messages from client"""
        try:
            async for data in ws.iter_json():
                if symbols := data.get("params", {}).get("symbols"):
                    if isinstance(symbols, str):
                        symbols = symbols.split(",")
                    
                    subscribed_symbols.clear()
                    subscribed_symbols.update(s.strip() for s in symbols if s.strip())
                    logger.info(f"WebSocket subscribed to symbols: {subscribed_symbols}")

        except WebSocketDisconnect:
            pass
        except RuntimeError:
            await ws.close()

    async def producer_handler(ws: WebSocket):
        """Send live updates to client"""
        try:
            while websocket.client_state != WebSocketState.DISCONNECTED:
                if subscribed_symbols:
                    # Get updated data for subscribed symbols
                    current_symbols = list(subscribed_symbols)
                    np.random.shuffle(current_symbols)  # Randomize update order
                    
                    # Send updates for a few symbols at a time
                    for symbol in current_symbols[:3]:  # Update 3 symbols per cycle
                        try:
                            symbol_data = get_live_position_data([symbol])
                            if len(symbol_data) > 0:
                                row = symbol_data.iloc[0]
                                update = {
                                    "Ticker": symbol,
                                    "Price": float(row['Price']),
                                    "MarketValue": float(row['MarketValue']),
                                    "PnL_Day": float(row['PnL_Day'])
                                }
                                
                                # Clean any NaN or infinite values
                                for key, value in update.items():
                                    if pd.isna(value) or value == float('inf') or value == float('-inf'):
                                        update[key] = 0
                                
                                await ws.send_json(update)
                                await asyncio.sleep(np.random.uniform(0.3, 0.8))  # Random delay between updates
                        
                        except Exception as e:
                            logger.error(f"Error sending update for {symbol}: {str(e)}")
                            continue
                
                await asyncio.sleep(np.random.uniform(0.2, 0.5))  # Pause between cycles

        except WebSocketDisconnect:
            pass
        except RuntimeError:
            await ws.close()

    # Run both consumer and producer concurrently
    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))

    # Wait for either task to complete (usually due to disconnect)
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel remaining tasks
    for task in pending:
        task.cancel()

if __name__ == "__main__":
    logger.info("Starting Portfolio Analytics Widget Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True)