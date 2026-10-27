# IceQ — Cold-Chain Spoilage Analytics

**Protect Every Degree. Preserve Every Delivery.**

IceQ is a web-based cold-chain monitoring and spoilage-risk analytics prototype designed to monitor temperature readings from different storage units, identify temperature-limit violations, and display unit status through a centralized dashboard.

The current version uses **simulated sensor data and rule-based risk classification** to demonstrate the monitoring workflow. Physical IoT sensor integration and machine-learning-based prediction are future enhancements.

## Live Demo

- **Website:** https://ice-q-cold-chain-analytics.vercel.app/
- **Monitoring Dashboard:** https://ice-q-cold-chain-analytics.vercel.app/dashboard
- **Backend API:** https://iceq-cold-chain-analytics.onrender.com
- **API Documentation:** https://iceq-cold-chain-analytics.onrender.com/docs
- **GitHub Repository:** https://github.com/LourdhSanya/IceQ-Cold-Chain-Analytics

## Project Overview

Maintaining the correct temperature is important for preserving temperature-sensitive products during storage and transportation. Temperature deviations can increase spoilage risk and affect product quality.

IceQ demonstrates how a software-based monitoring system can process temperature readings, compare them against configured thresholds, classify unit status, and present monitoring information through a web dashboard.

## Key Features

- Simulated temperature sensor readings for multiple cold-chain storage units.
- Threshold-based risk classification into **NORMAL**, **WARNING**, and **CRITICAL** states.
- Monitoring dashboard displaying unit temperatures and status.
- Backend API for serving monitoring information.
- Cloud-hosted frontend and backend demonstration.
- Clear identification of simulated data in the demonstration interface.

## System Architecture

The prototype follows this workflow:

1. **Data Generation:** Generate simulated temperature readings for dairy, produce, and frozen-product units.
2. **Data Processing:** Organize and process readings for monitoring.
3. **Risk Classification:** Compare temperature readings against configured limits and classify the unit status.
4. **Backend API:** Use FastAPI to expose monitoring information.
5. **Frontend Dashboard:** Use React to display unit readings, status, and monitoring information.

**Workflow:** Simulated Sensor Data → Data Processing → Threshold-Based Risk Engine → FastAPI Backend → React Dashboard

## Dataset and Testing

The demonstration dataset contains:

- **6,048** simulated temperature readings.
- **3** example monitoring units.
- **7 days** of simulated data.
- **5-minute** reading intervals.

In the constructed simulation test, the threshold-checking process detected all **102 predefined simulated incident readings**, with zero missed incidents in that test.

This result describes the constructed simulation only. It is **not real-world prediction accuracy**, and it does not establish the performance of a trained machine-learning model.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Data Processing | Pandas, Python |
| Risk Classification | Configured threshold-based rules |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |
| API Testing and Documentation | FastAPI interactive API documentation |

## Current Limitations

- Sensor readings are simulated; physical IoT hardware is not integrated.
- Risk classification uses configured rules rather than a trained machine-learning model.
- Testing is based on constructed simulated scenarios, not real-world cold-chain operations.
- Production-grade alert delivery and persistent monitoring infrastructure are not yet established.

## Future Enhancements

- Integrate physical IoT temperature sensors and live sensor streams.
- Validate the system using real cold-chain datasets.
- Develop and evaluate machine-learning models when suitable labelled data is available.
- Add notification mechanisms for temperature-risk events.
- Improve data storage, monitoring history, and production reliability.

## Running the Project Locally

### Frontend

1. Clone the repository:

   ```bash
   git clone https://github.com/LourdhSanya/IceQ-Cold-Chain-Analytics.git
   ```

2. Navigate to the frontend project directory:

   ```bash
   cd IceQ-Cold-Chain-Analytics/frontend
   ```

   If your repository has a different folder structure, navigate to the directory containing the frontend `package.json` file.

3. Install dependencies:

   ```bash
   npm install
   ```

4. Start the development server:

   ```bash
   npm run dev
   ```

5. Open the local URL shown in the terminal, usually `http://localhost:5173`.

### Backend

The backend is hosted separately. To run it locally, navigate to the backend directory and follow its dependency and startup instructions. The exact commands depend on the files included in your backend setup.

## Project Status

**Current stage:** Working software prototype using simulated data and threshold-based risk classification.

IceQ demonstrates the core monitoring workflow through a web dashboard and backend API. Physical sensor integration, real-world validation, and machine-learning-based prediction remain future development goals.

---

Developed as a final-year computer science engineering project.
