# 🚔 **Los Angeles Crime Dashboard**

An interactive web dashboard to explore and analyze real-time crime statistics for Los Angeles. The dashboard leverages **Machine Learning (ML)**, **Natural Language Processing (NLP)**, and **interactive visualizations** to provide insights into crime trends, severity, and hotspots.

🔗 **📸 Demo Video**: [Los Angeles Crime Dashboard](https://drive.google.com/file/d/1CTCn4jtxZSflq7oKJ3U9HrCDrd7d3uDZ/view?usp=sharing)

## 🚀 **Features**

- 📊 **Area Crime Analysis**: Visualize crime stats in different neighborhoods.
- 🔍 **Comparative Crime Analysis**: Compare crime data across various regions.
- 🌍 **Geo Hotspots**: Detect geographic hotspots for crime in real-time.
- ⚖️ **Crime Severity Analyzer**: Assess and sort crimes by severity scores for better resource allocation.
- 📝 **Crime Summarizer**: Generate crime statistics summaries for specific areas.

## 🛠️ **Tech Stack**

- **Python 3.8**
- **Dash + Plotly** (for interactive data visualizations)
- **AWS EC2** (for app hosting)
- **AWS ECR** (for Docker image storage)
- **Docker** (for containerization)
- **Pandas** (for data processing)
- **NLTK** (for NLP tasks)

## 📦 **Deployment**

### To run locally using Docker:

```bash
# Build the Docker image
docker build -t crime-dashboard .

# Run the Docker container
docker run -p 8050:8050 crime-dashboard
```


