# Portfolio Analytics Widget for OpenBB

A comprehensive real-time portfolio analytics widget for OpenBB Workspace featuring 35,000+ positions with 200+ metrics in multiple view modes.

## 🚀 Features

### Data Scale
- **35,000 positions** with real-time updates
- **200+ metrics** including P&L, risk, ESG, and technical indicators
- **Real-time data streaming** with configurable update intervals
- **Large-scale performance** optimized for institutional portfolios

### View Modes

#### 1. Flat View (`/portfolio_analytics`)
- Complete portfolio data in tabular format
- Full column set with advanced filtering and sorting
- Real-time P&L and risk metric updates
- Color-coded liquidity flags and performance indicators

#### 2. Tree/Hierarchical View (`/portfolio_tree`)
- Drill-down structure: Fund → Strategy → PM → Portfolio
- Aggregated metrics at each hierarchy level
- Expandable/collapsible groups
- Position count and summary statistics

#### 3. Pivot View (`/portfolio_pivot`)
- Dynamic pivot table functionality
- Drag-and-drop column organization
- Multi-dimensional analysis by Fund, Strategy, Sector, Region
- Aggregation functions for key metrics

### Key Metrics
- **P&L**: Day, MTD, QTD, YTD, 1Y
- **Risk**: VaR (95%, 99%), Beta, Volatility, Sharpe, Sortino
- **Exposure**: ADV%, Days to Liquidate, Market Impact
- **Attributes**: Sector, Region, Currency, Liquidity Flags
- **Performance Attribution**: Factor exposures and contributions
- **ESG**: Scores, Carbon Intensity, Ratings
- **Technical**: RSI, MACD, Bollinger Bands, Moving Averages

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- OpenBB Workspace access

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd rt-pivot-obb-widget
pip install -r requirements.txt
```

2. **Start the Widget Server**
```bash
python main.py
```

The server will start on `http://localhost:8020`

3. **Verify Installation**
```bash
python test_widget.py
```

### OpenBB Integration

1. **Access Widget Configuration**
   - Navigate to: `http://localhost:8020/widgets.json`
   - This endpoint provides the widget configurations for OpenBB

2. **Add to OpenBB Workspace**
   - In OpenBB Workspace, add a custom widget source
   - Use the base URL: `http://localhost:8020`
   - The three portfolio widgets will become available

3. **Available Widgets**
   - Portfolio Analytics - Flat View
   - Portfolio Analytics - Tree View  
   - Portfolio Analytics - Pivot View

## 📊 Widget Configuration

### Real-time Updates
- **Refresh Interval**: 5 seconds
- **Stale Time**: 30 seconds
- **Auto-refresh**: Enabled for all views

### AGGrid Features
- **Column Management**: Resizable, sortable, filterable
- **Row Grouping**: Enabled for hierarchical analysis
- **Pivot Mode**: Full pivot table functionality
- **Export**: Data export capabilities
- **Charts**: Built-in chart generation from selected data

### Performance Optimizations
- **Streaming Updates**: Only modified positions updated
- **Column Virtualization**: Handles 200+ columns efficiently
- **Row Virtualization**: Handles 35,000+ rows smoothly
- **Memory Management**: Optimized data structures

## 🏗️ Architecture

### Backend Components

#### `main.py`
- FastAPI application with CORS configuration
- Widget registration and endpoint definitions
- Three main widget endpoints with real-time data

#### `data_generator.py`
- `PortfolioDataGenerator` class for large-scale data generation
- Real-time update simulation with market-like behavior
- Thread-safe data management
- Hierarchical data structure support

#### Widget Endpoints
- `/portfolio_analytics` - Flat view with all metrics
- `/portfolio_tree` - Hierarchical view with aggregation
- `/portfolio_pivot` - Pivot table optimized data
- `/real_time_updates` - Real-time summary metrics

### Data Structure

#### Base Metrics (Core Portfolio Data)
```python
{
    "Fund": "GlobalEq",
    "Strategy": "L/S Equity", 
    "PM": "Jane Doe",
    "Portfolio": "Alpha Growth",
    "Ticker": "AAPL",
    "Quantity": 42500,
    "Price": 185.92,
    "MarketValue": 7890000,
    "PnL_Day": 125400,
    "PnL_MTD": 512300,
    "VaR_95": 640000,
    "Beta": 1.15,
    "ADV%": 8.2,
    "LiquidityFlag": "OK"
}
```

#### Extended Metrics (200+ Columns)
- Performance attribution across multiple time periods
- Risk factor exposures and attributions
- Trading and liquidity metrics
- ESG scores and ratings
- Stress test results
- Technical indicators
- Options Greeks
- Macro sensitivity factors

## 🔧 Customization

### Modify Data Scale
```python
# In main.py, change the row count
data = portfolio_generator.generate_portfolio_data(50000)  # Increase to 50k
```

### Add Custom Metrics
```python
# In data_generator.py, extend _generate_extended_metrics()
df["Custom_Metric"] = np.random.uniform(0, 100, len(df))
```

### Adjust Update Frequency
```python
# In widget configuration
"refetchInterval": 2000,  # 2 seconds
"staleTime": 60000,       # 1 minute
```

## 📈 Performance Considerations

### Memory Usage
- **35,000 rows × 200 columns**: ~150-300 MB RAM
- **Real-time updates**: Minimal additional overhead
- **Client-side rendering**: AGGrid handles virtualization

### Update Performance
- **5% of positions updated per cycle** (configurable)
- **Thread-safe operations** for concurrent access
- **Optimized data structures** for fast aggregation

### Network Optimization
- **JSON compression** for large datasets
- **Incremental updates** for real-time data
- **Client-side caching** with stale time management

## 🛡️ Production Considerations

### Security
- CORS configured for OpenBB domains
- No authentication required (add as needed)
- Data validation and error handling

### Scalability
- Horizontal scaling with load balancers
- Database integration for persistent data
- Redis for real-time data distribution

### Monitoring
- Health check endpoint at `/health`
- Logging configuration for debugging
- Performance metrics tracking

## 📋 API Endpoints

| Endpoint | Description | Returns |
|----------|-------------|---------|
| `/` | Root information | Service details |
| `/health` | Health check | Status and timestamp |
| `/widgets.json` | Widget configurations | OpenBB widget definitions |
| `/portfolio_analytics` | Flat portfolio view | 35k rows with all metrics |
| `/portfolio_tree` | Hierarchical view | Grouped data with aggregations |
| `/portfolio_pivot` | Pivot table data | Subset optimized for pivoting |
| `/real_time_updates` | Summary metrics | Real-time portfolio totals |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the test script output: `python test_widget.py`
2. Verify server logs for error messages
3. Ensure OpenBB Workspace connectivity
4. Review widget configuration in `/widgets.json`

---

**Built for OpenBB Workspace** - Delivering institutional-grade portfolio analytics with real-time performance monitoring.