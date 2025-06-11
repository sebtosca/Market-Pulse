# Market Pulse AI

A sophisticated market analysis tool that leverages AI to provide comprehensive insights into life sciences companies and market opportunities.

## Overview

Market Pulse AI is a web application that combines three specialized AI agents to analyze companies and market opportunities in the life sciences sector. The system processes input (either company names or press release URLs) and generates detailed reports with strategic recommendations.

## Installation

### Option 1: Docker (Recommended)

1. Install Docker and Docker Compose:
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

2. Clone the repository:
```bash
git clone https://github.com/sebtosca/Market-Pulse.git
cd Market-Pulse
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8050`

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/sebtosca/Market-Pulse
cd Market-Pulse
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
1.
pip install ollama 
2.
ollama pull mistral
ollama pull openhermes


4. Run the application:
```bash
python market_pulse_app.py
```

The application will be available at `http://localhost:8050`

# Important Info !!! 
Running a company name will take more time, URL will run faster. 
Crawler will take a bit of time to start as it tries finding a valid url 

## Usage

1. Launch the application
2. Choose input type (Company Name or Press Release URL) -> Important Info !!!
3. Enter the target company name or URL
4. Click "Analyze" to start the process
5. Monitor real-time progress of the three agents
6. View the generated report with strategic recommendations

## Architecture

### Core Components

1. **Crawler Agent**
   - Responsible for data collection and extraction
   - Processes both company names and press release URLs
   - Implements intelligent retry mechanisms and error handling
   - Uses configurable search parameters and scoring systems

2. **Analyst Agent**
   - Performs deep market analysis
   - Identifies therapeutic areas and mechanisms of action
   - Analyzes competitive landscape
   - Evaluates market trends and risk factors

3. **Advisor Agent**
   - Generates strategic recommendations
   - Creates comprehensive HTML reports
   - Provides actionable insights
   - Assesses market opportunities

### Technical Stack

- **Frontend**: Dash (Python web framework)
- **Backend**: Python
- **AI Components**: Custom agent implementations
- **Data Processing**: Structured data pipelines
- **UI/UX**: Modern, responsive design with real-time progress tracking

## Docker Support

The application is containerized using Docker for easy deployment and consistent environments across different machines.

### Docker Features

- Uses Python 3.11 slim image for optimal size and performance
- Includes all necessary system dependencies
- Automatically downloads required spaCy models
- Volume mounting for development
- Automatic restart on failure
- Environment variable support

### Docker Commands

Build and start the application:
```bash
docker-compose up --build
```

Run in detached mode:
```bash
docker-compose up -d
```

Stop the application:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

## AI Components and Tradeoffs

### AI Agent Design

1. **Modular Architecture**
   - Pros:
     - Independent agent operation
     - Easy to update or replace individual components
     - Scalable design
   - Cons:
     - Requires careful state management
     - Potential for communication overhead

2. **Data Processing**
   - Pros:
     - Structured data flow
     - Clear separation of concerns
     - Robust error handling
   - Cons:
     - Complex data transformation requirements
     - Need for extensive validation

3. **Report Generation**
   - Pros:
     - Rich, formatted output
     - Comprehensive insights
     - Professional presentation
   - Cons:
     - HTML generation complexity
     - Large output size

### AI-Assisted Development Reflection

Incorporating Generative AI into my development workflow significantly accelerated certain aspects of my project. It improved efficiency during the planning phase by allowing me to ask targeted questions and gain a clearer understanding of suitable models and frameworks. This facilitated a more structured approach to project design before writing any code. Additionally, AI tools helped generate file structures, organize project components, and produce boilerplate code, such as functions, loops, configuration files, and documentation like README files. These contributions enhanced both speed and organization throughout the development process.

However, the use of Generative AI also introduced challenges. In some cases, the output did not align with my original intent or the instructions I provided. This often required additional time to refine prompts and correct misaligned results, time that could have been better spent on core problem-solving tasks. Moreover, while AI expedited initial code generation, it frequently led to increased debugging efforts to ensure correctness and quality.

In summary, while Generative AI offers substantial advantages in terms of speed and support during early stages of development, it often shifts time and effort toward prompt engineering and quality assurance. It is a valuable tool, but its use requires careful oversight to truly enhance the development process.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors and users
- Special thanks to the AI development community
- Inspired by the need for better market analysis tools 