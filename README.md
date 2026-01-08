HemoSense - A Non Invasive Hemoglobin Estimation System

Problem:
Current diagnostic standards rely on painful needles, which generate biohazard waste, trigger Trypanophobia, and carry risks of blood-borne infections. Logistical delays and the requirement for skilled phlebotomists create systemic barriers to care in low-resource environments. HemoSense resolves these challenges by delivering instant, painless diagnostics through a simple sensor touch.

Proposed Solution:

HemoSense AI leverages the convergence of embedded hardware and cloud-based intelligence:

Perception Layer: An AS7265x Smart Spectral Triad sensor captures light attenuation across 18 discrete channels (410nm to 940nm) to generate a high-resolution "spectral fingerprint" of blood optical density.

Edge Processing: An Azure Sphere MT3620 MCU orchestrates secure data acquisition. Utilizing its hardware-rooted "Root of Trust," the device ensures "Sovereign-Ready" data integrity and chip-level encryption for all clinical telemetry.

The Brain (AI Layer): Predictive logic is powered by a VotingEnsemble regression model trained via Azure Automated ML (AutoML). The model was validated across 15,000 synthetic samples generated using the Beer-Lambert Law, achieving a high-precision Normalized RMSE of 0.11462.

Inclusive Design: To ensure diagnostic parity, the AI specifically accounts for skin tone variability by incorporating the Fitzpatrick Scale into the training foundation.

Cloud Deployment & Interface
The production model is hosted on an Azure Managed Online Endpoint (v2) in the South India region, providing sub-second inference latency. Real-time diagnostic feedback is served via a Streamlit dashboard, enabling immediate medical decision support.

This repository serves as a comprehensive manual for the HemoSense MVP, providing the end-to-end workflow from physics-based data synthesis to a fully operational, "Healthy" cloud endpoint.

"Ending the Needle. Delivering Health."
