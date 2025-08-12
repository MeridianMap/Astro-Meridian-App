# Jupyter Notebooks

Interactive Jupyter notebooks demonstrating various aspects of the Meridian Ephemeris API.

## Available Notebooks

### 1. Getting Started
**File**: [`01-getting-started.ipynb`](../../examples/notebooks/01-getting-started.ipynb)

A comprehensive introduction to the Meridian Ephemeris API covering:
- Basic API setup and connection
- Your first chart calculation
- Understanding response data
- Visualizing planetary positions
- Working with different input formats
- Error handling and validation
- Performance analysis

**Prerequisites**: `requests`, `pandas`, `matplotlib`, `seaborn`

### 2. Advanced Calculations *(Coming Soon)*
**File**: `02-advanced-calculations.ipynb`

Advanced astrological calculation techniques:
- Multiple house systems comparison
- Aspect calculations and orbs
- Fixed star positions
- Retrograde motion analysis
- Chart rectification techniques

### 3. Batch Processing *(Coming Soon)*
**File**: `03-batch-processing.ipynb`

Efficiently processing multiple charts:
- Bulk chart calculations
- Performance optimization
- Parallel processing
- Caching strategies
- Rate limit management

### 4. Data Analysis *(Coming Soon)*
**File**: `04-data-analysis.ipynb`

Statistical analysis of astrological data:
- Planetary distribution patterns
- House system statistics
- Sign and element analysis
- Correlation studies
- Visualization techniques

### 5. Web Integration *(Coming Soon)*
**File**: `05-web-integration.ipynb`

Building web applications with the API:
- Flask/FastAPI integration
- Real-time chart calculations
- Chart visualization
- User authentication
- Database integration

## Running the Notebooks

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/meridian-ephemeris/api.git
   cd api/examples/notebooks
   ```

2. **Install dependencies**:
   ```bash
   pip install jupyter pandas matplotlib seaborn requests
   ```

3. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

4. **Open a notebook** and start exploring!

### Google Colab

Run notebooks directly in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/meridian-ephemeris/api/blob/main/examples/notebooks/01-getting-started.ipynb)

### Binder

Launch an interactive environment with Binder:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/meridian-ephemeris/api/main?filepath=examples%2Fnotebooks)

## Notebook Features

Each notebook includes:

- **📚 Educational Content**: Detailed explanations of astrological concepts
- **💻 Code Examples**: Practical, runnable code samples
- **📊 Visualizations**: Charts and graphs to understand data
- **🔧 Error Handling**: Robust error handling examples
- **📝 Exercises**: Interactive exercises to practice concepts
- **🔗 References**: Links to additional resources

## API Configuration

All notebooks use a configurable API endpoint:

```python
# For local development
BASE_URL = "http://localhost:8000"

# For production
BASE_URL = "https://api.meridianephemeris.com"
```

## Data Requirements

Notebooks include sample data, but you can use your own:

```python
# Example birth data
sample_data = {
    "name": "Your Name",
    "datetime": {"iso_string": "1990-06-15T14:30:00"},
    "latitude": {"decimal": 40.7128},
    "longitude": {"decimal": -74.0060},
    "timezone": {"name": "America/New_York"}
}
```

## Visualization Examples

### Zodiac Wheel
```python
# Create a zodiac wheel visualization
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
angles = [planet['longitude'] * np.pi / 180 for planet in planets.values()]
ax.scatter(angles, [1] * len(angles))
```

### House Distribution
```python
# Plot planets by house
house_counts = df['house'].value_counts()
plt.bar(house_counts.index, house_counts.values)
plt.xlabel('House')
plt.ylabel('Planet Count')
```

### Sign Elements
```python
# Element distribution pie chart
element_counts = df['element'].value_counts()
plt.pie(element_counts.values, labels=element_counts.index)
```

## Common Use Cases

The notebooks demonstrate solutions for:

- **Astrologers**: Professional chart calculation and analysis
- **Developers**: API integration and application development  
- **Researchers**: Statistical analysis of astrological patterns
- **Students**: Learning astrological programming concepts
- **Enthusiasts**: Personal chart exploration and understanding

## Contributing

Help improve the notebooks:

1. **Report Issues**: Found a bug or error? [Open an issue](https://github.com/meridian-ephemeris/api/issues)
2. **Suggest Notebooks**: Ideas for new notebooks? Let us know!
3. **Submit Improvements**: Send pull requests with enhancements
4. **Share Examples**: Show us what you've built!

## Troubleshooting

### Common Issues

**API Connection Failed**
- Check that the API server is running
- Verify the correct BASE_URL is set
- Check network connectivity

**Missing Dependencies**
- Install all required packages: `pip install -r requirements.txt`
- Update outdated packages: `pip install --upgrade package-name`

**Visualization Issues**
- Ensure matplotlib backend is properly configured
- For Jupyter: `%matplotlib inline`
- For interactive plots: `%matplotlib widget`

**Rate Limiting**
- Add delays between API calls: `time.sleep(1)`
- Implement proper retry logic
- Cache results to avoid redundant calls

### Getting Help

- 📧 Email: [support@meridianephemeris.com](mailto:support@meridianephemeris.com)
- 💬 Discussions: [GitHub Discussions](https://github.com/meridian-ephemeris/api/discussions)
- 📚 Documentation: [API Reference](../api/overview.md)
- 🐛 Issues: [Report Problems](https://github.com/meridian-ephemeris/api/issues)

## Next Steps

After working through the notebooks:

1. **Explore the API**: Try the [interactive documentation](https://api.meridianephemeris.com/docs)
2. **Use Client SDKs**: Install the [Python](../reference/python-sdk.md) or [TypeScript](../reference/typescript-sdk.md) SDK
3. **Build Applications**: Create your own astrological tools
4. **Join Community**: Connect with other developers and astrologers

---

*Happy calculating! 🌟*