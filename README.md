# 🤖 Agentic AI Intrusion Detection System

**A state-of-the-art security framework leveraging Machine Learning and Game Theory to defend web applications against both known and zero-day cyber threats.**


## 🚀 Project Snapshot

This project implements a novel, **Agentic AI-driven security framework** designed to protect web applications by intelligently adapting its defense posture based on modeled attacker behavior.

This framework uniquely combines:
*   **Deep Learning Anomaly Detection (Autoencoder)**, which is intelligently tuned by...
*   **Game Theory (Nash Equilibrium)** for adaptive, proactive defense adjustments.


## 🛡️ Key Features & Technologies

### **Hybrid Detection Engine**
*   **Module A (Known Attacks):** Leverages a high-performance **Keras Dense Neural Network** for fast, accurate classification of known attack signatures (e.g., SQLi, XSS, based on NSL-KDD features).
*   **Module B (Unknown Threats):** Employs a **Keras Autoencoder** trained on normal traffic to detect novel/zero-day threats via high reconstruction error.

### **Adaptive Defense Strategy (The Agentic Core)**
*   **Module C (Game-Theoretic Defender Agent):** Implements strategic modeling of attacker-defender interactions using a **Payoff Matrix**.
*   This logic calculates the **Nash Equilibrium** to dynamically adjust the Autoencoder's detection threshold ($\mathbf{T^*}$), ensuring a **proactive and adaptive defense posture** that minimizes risk.

### **Real-Time Proxy Simulation**
*   Built using **Flask**, the system is structured to act as a security gateway capable of intercepting, analyzing, and blocking malicious HTTP traffic in real-time.

### **Verified Performance**
*   Initial validation performed on the **NSL-KDD dataset**, demonstrating the framework's capability to achieve competitive detection accuracy while providing a more **enhanced defense posture** compared to static Intrusion Detection Systems (IDS).



## 🛠️ Built With

| Category | Technologies |
| :--- | :--- |
| **AI/ML** | TensorFlow/Keras (Autoencoders, Dense Networks), Scikit-learn (Preprocessing) |
| **Strategy/Math** | NumPy (for Game Theory payoff matrix calculation and solving) |
| **Web/Deployment**| Flask (for real-time proxy simulation) |

Here is the Agentic AI Intrusion Detection System Images:
<img width="1756" height="807" alt="image" src="https://github.com/user-attachments/assets/a0757414-1801-4151-a3ac-4f905650adae" />
<img width="1804" height="832" alt="image" src="https://github.com/user-attachments/assets/3e90deb6-593f-45c3-8649-326ece37d9a1" />
<img width="1775" height="794" alt="image" src="https://github.com/user-attachments/assets/0c21fecc-5888-4faf-81ec-9e807aa575cf" />
<img width="1753" height="783" alt="image" src="https://github.com/user-attachments/assets/d0e87f53-ca51-4f69-bedf-d306edc8421a" />
<img width="1807" height="798" alt="image" src="https://github.com/user-attachments/assets/00a37429-b90c-47aa-852b-c84cac98186a" />
