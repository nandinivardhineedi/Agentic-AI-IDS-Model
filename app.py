# # # # app.py - The Agentic AI Intrusion Detection Server (FINAL REAL-TIME PROXY VERSION)

# # # import pickle
# # # import numpy as np
# # # import tensorflow as tf
# # # import pandas as pd  # kept for future use if needed
# # # from flask import Flask, request, render_template, jsonify
# # # import time  # Needed for time-based features

# # # # --- GLOBAL VARIABLES & MODEL LOADING ---
# # # app = Flask(__name__, template_folder='templates')
# # # MODEL_PATH = 'model_classifier.keras'
# # # AE_MODEL_PATH = 'model_autoencoder.keras'
# # # ASSETS_PATH = 'preprocessing_assets.pkl'

# # # try:
# # #     # Load Models
# # #     model_clf = tf.keras.models.load_model(MODEL_PATH)
# # #     autoencoder = tf.keras.models.load_model(AE_MODEL_PATH)

# # #     # Load Preprocessing Assets
# # #     with open(ASSETS_PATH, 'rb') as f:
# # #         assets = pickle.load(f)

# # #     scaler_fit = assets['scaler']
# # #     feature_names = assets['feature_names']  # full feature space (e.g., 119)
# # #     adaptive_threshold = assets['adaptive_threshold']  # baseline AE threshold from Colab

# # #     # Baseline threshold used before game-theoretic adjustment
# # #     T_normal_baseline = adaptive_threshold

# # #     # --- Get the TRUE number of input features from the models (should be 119) ---
# # #     n_model_features_clf = model_clf.input_shape[-1]
# # #     n_model_features_ae = autoencoder.input_shape[-1]

# # #     if n_model_features_clf != n_model_features_ae:
# # #         print(
# # #             f"WARNING: Classifier expects {n_model_features_clf} features, "
# # #             f"autoencoder expects {n_model_features_ae} features."
# # #         )

# # #     # Use classifier input size as canonical
# # #     N_FEATURES = n_model_features_clf
# # #     print(f"Model input dimension (N_FEATURES) = {N_FEATURES}")

# # #     # Optional: print scaler expected features (likely 38 in your case)
# # #     if hasattr(scaler_fit, "n_features_in_"):
# # #         print(f"Scaler expects {scaler_fit.n_features_in_} features as input")
# # #     else:
# # #         print("Scaler has no n_features_in_ attribute; will treat as generic transformer.")

# # #     # Optional: disable strict feature-name checking; we use raw NumPy arrays
# # #     try:
# # #         if hasattr(scaler_fit, "feature_names_in_"):
# # #             del scaler_fit.feature_names_in_
# # #     except Exception as e:
# # #         print(f"Warning: could not remove feature_names_in_ from scaler: {e}")

# # #     print("--- Models and Assets Loaded Successfully ---")

# # # except Exception as e:
# # #     print(f"CRITICAL ERROR: Could not load one or more assets: {e}")
# # #     exit(1)


# # # # --- FEATURE EXTRACTION (Now attempting to process request data) ---
# # # def extract_and_process_features(request_obj):
# # #     payload = request_obj.form.get('payload', '').strip().lower()
# # #     url = request_obj.url.lower()
# # #     method = request_obj.method  # reserved for future use (e.g., mapping HTTP method)

# # #     # Create base numeric feature vector with the EXACT size required by the models (e.g., 119)
# # #     feature_vector = np.zeros(N_FEATURES, dtype=np.float32)

# # #     # --- SIMULATED MAPPING TO FEATURES (MUST BE CUSTOMIZED FOR REAL ACCURACY) ---

# # #     # 1. Simulate Numeric Features
# # #     # Feature 0 (Proxy for size/count): Use payload length
# # #     if N_FEATURES > 0:
# # #         feature_vector[0] = min(len(payload) / 500.0, 5.0)

# # #     # Feature 1 (Proxy for Data Volume): Use URL length
# # #     if N_FEATURES > 1:
# # #         feature_vector[1] = min(len(url) / 50.0, 5.0)

# # #     # Feature 2 (Proxy for Time/Entropy): Use a time-based feature (simulated)
# # #     if N_FEATURES > 2:
# # #         feature_vector[2] = (time.time() % 100) / 100.0

# # #     # 2. Simulate Categorical / Indicator Features
# # #     # For known suspicious patterns (e.g., simple SQLi pattern)
# # #     if 'union select' in payload or 'or 1=1' in payload:
# # #         # Choose some stable indicator index within the available feature dimension
# # #         indicator_index = 100  # arbitrary but <= N_FEATURES-1
# # #         if N_FEATURES > indicator_index:
# # #             feature_vector[indicator_index] = 1.0

# # #     # --- END TEMPORARY MAPPING ---

# # #     # Reshape to (1, n_features) for scaler and models
# # #     feature_vector_2d = feature_vector.reshape(1, -1)

# # #     # Apply scaler ONLY if it is compatible with the model input dimension
# # #     use_scaler = hasattr(scaler_fit, "n_features_in_") and scaler_fit.n_features_in_ == N_FEATURES
# # #     if use_scaler:
# # #         X_scaled = scaler_fit.transform(feature_vector_2d)
# # #     else:
# # #         # For now, we skip scaling if incompatible (e.g., scaler was fit on 38 features only).
# # #         # This keeps the system running; values are still bounded by our manual feature engineering.
# # #         X_scaled = feature_vector_2d

# # #     # Crucial: Ensure the final vector is the correct type for Keras
# # #     return X_scaled.astype(np.float32)


# # # # --- NEW: Function to Solve the Game Based On an Attack Probability Vector ---
# # # def solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob):
# # #     """Calculates the optimal defender strategy (D*) based on assumed attack distribution."""
# # #     num_defender_actions = payoff_matrix.shape[1]
# # #     expected_defender_payoffs = np.zeros(num_defender_actions)

# # #     for j in range(num_defender_actions):
# # #         expected_payoff = np.dot(attack_distribution_prob, payoff_matrix[:, j])
# # #         expected_defender_payoffs[j] = expected_payoff

# # #     optimal_defender_strategy_index = np.argmax(expected_defender_payoffs)

# # #     # Map index (0 or 1) to the adaptive factor (D2 = 0.8, D1 = 1.2)
# # #     if optimal_defender_strategy_index == 1:  # D2 (Low Threshold/Aggressive)
# # #         adaptive_factor = 0.8
# # #     else:  # D1 (High Threshold/Conservative)
# # #         adaptive_factor = 1.2

# # #     return adaptive_factor, optimal_defender_strategy_index


# # # # --- SECURITY AGENT LOGIC (Module C guides B, A runs independently) ---
# # # def agentic_decision(feature_vector, payload):
# # #     # 1. MODULE A: Known Attack Detection (Keras Classifier)
# # #     prediction = model_clf.predict(feature_vector, verbose=0)
# # #     predicted_class_index = np.argmax(prediction)
# # #     is_known_attack = predicted_class_index != 0

# # #     # 2. MODULE B: Unknown Attack Detection (Autoencoder)
# # #     reconstruction = autoencoder.predict(feature_vector, verbose=0)
# # #     mse = np.mean(np.power(feature_vector - reconstruction, 2), axis=1)[0]

# # #     # 3. MODULE C: DYNAMIC Adaptive Threshold (The Agentic Part)
# # #     payoff_matrix = np.array([
# # #         [2, 5],
# # #         [4, 8]
# # #     ])  # Conceptual Payoff Matrix

# # #     # *** SIMULATION STEP ***: Agent assesses current threat landscape (e.g., 50/50 mix)
# # #     attack_distribution_prob = np.array([0.5, 0.5])
# # #     adaptive_factor, strategy_idx = solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob)

# # #     global T_normal_baseline
# # #     T_star = T_normal_baseline * adaptive_factor
# # #     is_unknown_attack = mse > T_star

# # #     # --- FINAL DECISION (Standard Flow: Block if ANY detector triggers) ---

# # #     if is_known_attack:
# # #         return True, "BLOCKED", f"Known Attack Detected (Module A). Predicted class index: {predicted_class_index}"

# # #     if is_unknown_attack:
# # #         return True, "BLOCKED", (
# # #             f"Unknown Attack Detected (Module B). "
# # #             f"MSE: {mse:.4f} > T*: {T_star:.4f} (strategy_index={strategy_idx})"
# # #         )

# # #     # Default: If neither is triggered, allow access.
# # #     return False, "ALLOWED", f"Normal Traffic. (MSE: {mse:.4f}, T*: {T_star:.4f})"


# # # # --- WEB SERVER ROUTES ---
# # # @app.route('/')
# # # def index():
# # #     return render_template('index.html')


# # # @app.route('/submit_test', methods=['POST'])
# # # def submit_test():
# # #     try:
# # #         # CORE AGENT EXECUTION
# # #         feature_vector = extract_and_process_features(request)
# # #         payload = request.form.get('payload', '').strip().lower()

# # #         is_blocked, status, reason = agentic_decision(feature_vector, payload)

# # #         if is_blocked:
# # #             return jsonify({"status": status, "reason": reason}), 403
# # #         else:
# # #             return jsonify({"status": status, "reason": reason}), 200

# # #     except Exception as e:
# # #         # Helpful debugging info in JSON
# # #         return jsonify({"status": "ERROR", "reason": str(e)}), 500


# # # if __name__ == '__main__':
# # #     # Run the Flask app
# # #     app.run(debug=True)


# # # app.py - The Agentic AI Intrusion Detection Server (FINAL REAL-TIME PROXY VERSION)

# # import pickle
# # import numpy as np
# # import tensorflow as tf
# # import pandas as pd  # kept for future use if needed
# # from flask import Flask, request, render_template, jsonify
# # import time  # Needed for time-based features

# # # --- GLOBAL VARIABLES & MODEL LOADING ---
# # app = Flask(__name__, template_folder='templates')
# # MODEL_PATH = 'model_classifier.keras'
# # AE_MODEL_PATH = 'model_autoencoder.keras'
# # ASSETS_PATH = 'preprocessing_assets.pkl'

# # # Classifier confidence threshold: only treat as "known attack" if probability is high
# # CLF_ATTACK_PROB_THRESHOLD = 0.80  # you can tune this (e.g., 0.7–0.9)

# # try:
# #     # Load Models
# #     model_clf = tf.keras.models.load_model(MODEL_PATH)
# #     autoencoder = tf.keras.models.load_model(AE_MODEL_PATH)

# #     # Load Preprocessing Assets
# #     with open(ASSETS_PATH, 'rb') as f:
# #         assets = pickle.load(f)

# #     scaler_fit = assets['scaler']
# #     feature_names = assets['feature_names']  # full feature space (e.g., 119)
# #     adaptive_threshold = assets['adaptive_threshold']  # baseline AE threshold from Colab

# #     # Baseline threshold used before game-theoretic adjustment
# #     T_normal_baseline = adaptive_threshold

# #     # --- Get the TRUE number of input features from the models (should be 119) ---
# #     n_model_features_clf = model_clf.input_shape[-1]
# #     n_model_features_ae = autoencoder.input_shape[-1]

# #     if n_model_features_clf != n_model_features_ae:
# #         print(
# #             f"WARNING: Classifier expects {n_model_features_clf} features, "
# #             f"autoencoder expects {n_model_features_ae} features."
# #         )

# #     # Use classifier input size as canonical
# #     N_FEATURES = n_model_features_clf
# #     print(f"Model input dimension (N_FEATURES) = {N_FEATURES}")

# #     # Optional: print scaler expected features (likely 38 in your case)
# #     if hasattr(scaler_fit, "n_features_in_"):
# #         print(f"Scaler expects {scaler_fit.n_features_in_} features as input")
# #     else:
# #         print("Scaler has no n_features_in_ attribute; will treat as generic transformer.")

# #     # Optional: disable strict feature-name checking; we use raw NumPy arrays
# #     try:
# #         if hasattr(scaler_fit, "feature_names_in_"):
# #             del scaler_fit.feature_names_in_
# #     except Exception as e:
# #         print(f"Warning: could not remove feature_names_in_ from scaler: {e}")

# #     print("--- Models and Assets Loaded Successfully ---")

# # except Exception as e:
# #     print(f"CRITICAL ERROR: Could not load one or more assets: {e}")
# #     exit(1)


# # # --- FEATURE EXTRACTION (Now attempting to process request data) ---
# # def extract_and_process_features(request_obj):
# #     payload = request_obj.form.get('payload', '').strip().lower()
# #     url = request_obj.url.lower()
# #     method = request_obj.method  # reserved for future use (e.g., mapping HTTP method)

# #     # Create base numeric feature vector with the EXACT size required by the models (e.g., 119)
# #     feature_vector = np.zeros(N_FEATURES, dtype=np.float32)

# #     # --- SIMULATED MAPPING TO FEATURES (MUST BE CUSTOMIZED FOR REAL ACCURACY) ---

# #     # 1. Simulate Numeric Features
# #     # Feature 0 (Proxy for size/count): Use payload length
# #     if N_FEATURES > 0:
# #         feature_vector[0] = min(len(payload) / 500.0, 5.0)

# #     # Feature 1 (Proxy for Data Volume): Use URL length
# #     if N_FEATURES > 1:
# #         feature_vector[1] = min(len(url) / 50.0, 5.0)

# #     # Feature 2 (Proxy for Time/Entropy): Use a time-based feature (simulated)
# #     if N_FEATURES > 2:
# #         feature_vector[2] = (time.time() % 100) / 100.0

# #     # 2. Simulate Categorical / Indicator Features
# #     # For known suspicious patterns (e.g., simple SQLi pattern)
# #     if 'union select' in payload or 'or 1=1' in payload:
# #         # Choose some stable indicator index within the available feature dimension
# #         indicator_index = 100  # arbitrary but <= N_FEATURES-1
# #         if N_FEATURES > indicator_index:
# #             feature_vector[indicator_index] = 1.0

# #     # --- END TEMPORARY MAPPING ---

# #     # Reshape to (1, n_features) for scaler and models
# #     feature_vector_2d = feature_vector.reshape(1, -1)

# #     # Apply scaler ONLY if it is compatible with the model input dimension
# #     use_scaler = hasattr(scaler_fit, "n_features_in_") and scaler_fit.n_features_in_ == N_FEATURES
# #     if use_scaler:
# #         X_scaled = scaler_fit.transform(feature_vector_2d)
# #     else:
# #         # For now, we skip scaling if incompatible (e.g., scaler was fit on 38 features only).
# #         X_scaled = feature_vector_2d

# #     # Crucial: Ensure the final vector is the correct type for Keras
# #     return X_scaled.astype(np.float32)


# # # --- NEW: Function to Solve the Game Based On an Attack Probability Vector ---
# # def solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob):
# #     """Calculates the optimal defender strategy (D*) based on assumed attack distribution."""
# #     num_defender_actions = payoff_matrix.shape[1]
# #     expected_defender_payoffs = np.zeros(num_defender_actions)

# #     for j in range(num_defender_actions):
# #         expected_payoff = np.dot(attack_distribution_prob, payoff_matrix[:, j])
# #         expected_defender_payoffs[j] = expected_payoff

# #     optimal_defender_strategy_index = np.argmax(expected_defender_payoffs)

# #     # Map index (0 or 1) to the adaptive factor (D2 = 0.8, D1 = 1.2)
# #     if optimal_defender_strategy_index == 1:  # D2 (Low Threshold/Aggressive)
# #         adaptive_factor = 0.8
# #     else:  # D1 (High Threshold/Conservative)
# #         adaptive_factor = 1.2

# #     return adaptive_factor, optimal_defender_strategy_index


# # # --- SECURITY AGENT LOGIC (Module C guides B, A runs independently) ---
# # def agentic_decision(feature_vector, payload):
# #     # 1. MODULE A: Known Attack Detection (Keras Classifier)
# #     prediction = model_clf.predict(feature_vector, verbose=0)[0]  # shape: (num_classes,)
# #     predicted_class_index = int(np.argmax(prediction))
# #     max_prob = float(np.max(prediction))

# #     # Treat as "known attack" ONLY if:
# #     #  - not class 0 (BENIGN / NORMAL)
# #     #  - AND probability is high (>= CLF_ATTACK_PROB_THRESHOLD)
# #     is_known_attack_high_conf = (predicted_class_index != 0) and (max_prob >= CLF_ATTACK_PROB_THRESHOLD)

# #     # 2. MODULE B: Unknown Attack Detection (Autoencoder)
# #     reconstruction = autoencoder.predict(feature_vector, verbose=0)
# #     mse = float(np.mean(np.power(feature_vector - reconstruction, 2), axis=1)[0])

# #     # 3. MODULE C: DYNAMIC Adaptive Threshold (The Agentic Part)
# #     payoff_matrix = np.array([
# #         [2, 5],
# #         [4, 8]
# #     ])  # Conceptual Payoff Matrix

# #     # *** SIMULATION STEP ***: Agent assesses current threat landscape (e.g., 50/50 mix)
# #     attack_distribution_prob = np.array([0.5, 0.5])
# #     adaptive_factor, strategy_idx = solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob)

# #     global T_normal_baseline
# #     T_star = float(T_normal_baseline * adaptive_factor)
# #     is_unknown_attack = mse > T_star

# #     # 4. Simple signature-based override for very obvious attacks (still dynamic, not per-string)
# #     payload_lower = payload.lower()
# #     is_signature_attack = any(
# #         kw in payload_lower
# #         for kw in [
# #             "union select",
# #             " or 1=1",
# #             "' or '1'='1",
# #             "\" or \"1\"=\"1",
# #             "drop table",
# #             "xp_cmdshell",
# #         ]
# #     )

# #     # --- FINAL DECISION (Standard Flow) ---
# #     # Priority:
# #     #   (a) Strong signature -> BLOCK
# #     #   (b) High-confidence known attack + AE anomaly -> BLOCK
# #     #   (c) High-confidence known attack (even if AE normal) -> BLOCK
# #     #   (d) Unknown attack by AE alone -> BLOCK
# #     #   (e) Otherwise -> ALLOW

# #     if is_signature_attack:
# #         return True, "BLOCKED", (
# #             "Signature-based SQLi detection triggered. "
# #             f"(payload matched known attack pattern; MSE={mse:.4f}, T*={T_star:.4f})"
# #         )

# #     if is_known_attack_high_conf and is_unknown_attack:
# #         return True, "BLOCKED", (
# #             "High-confidence Known Attack + AE anomaly. "
# #             f"(class={predicted_class_index}, prob={max_prob:.3f}, MSE={mse:.4f} > T*={T_star:.4f})"
# #         )

# #     if is_known_attack_high_conf:
# #         return True, "BLOCKED", (
# #             "High-confidence Known Attack (Module A). "
# #             f"(class={predicted_class_index}, prob={max_prob:.3f}, MSE={mse:.4f}, T*={T_star:.4f})"
# #         )

# #     if is_unknown_attack:
# #         return True, "BLOCKED", (
# #             "Unknown Attack Detected (Module B - Autoencoder). "
# #             f"(MSE={mse:.4f} > T*={T_star:.4f}, classifier_class={predicted_class_index}, "
# #             f"class_prob={max_prob:.3f})"
# #         )

# #     # Default: If neither high-confidence classifier nor AE triggers, allow access.
# #     return False, "ALLOWED", (
# #         f"Normal / Low-Risk Traffic. "
# #         f"(class={predicted_class_index}, prob={max_prob:.3f}, MSE={mse:.4f}, T*={T_star:.4f})"
# #     )


# # # --- WEB SERVER ROUTES ---
# # @app.route('/')
# # def index():
# #     return render_template('index.html')


# # @app.route('/submit_test', methods=['POST'])
# # def submit_test():
# #     try:
# #         # CORE AGENT EXECUTION
# #         feature_vector = extract_and_process_features(request)
# #         payload = request.form.get('payload', '').strip()

# #         is_blocked, status, reason = agentic_decision(feature_vector, payload)

# #         if is_blocked:
# #             return jsonify({"status": status, "reason": reason}), 403
# #         else:
# #             return jsonify({"status": status, "reason": reason}), 200

# #     except Exception as e:
# #         # Helpful debugging info in JSON
# #         return jsonify({"status": "ERROR", "reason": str(e)}), 500


# # if __name__ == '__main__':
# #     # Run the Flask app
# #     app.run(debug=True)


# # app.py - The Agentic AI Intrusion Detection Server (FINAL REAL-TIME PROXY VERSION)

# import pickle
# import numpy as np
# import tensorflow as tf
# import pandas as pd  # kept for future use if needed
# from flask import Flask, request, render_template, jsonify
# import time  # Needed for time-based features

# # --- GLOBAL VARIABLES & MODEL LOADING ---
# app = Flask(__name__, template_folder='templates')
# MODEL_PATH = 'model_classifier.keras'
# AE_MODEL_PATH = 'model_autoencoder.keras'
# ASSETS_PATH = 'preprocessing_assets.pkl'

# # Classifier confidence threshold: only treat as "known attack" if probability is high
# CLF_ATTACK_PROB_THRESHOLD = 0.80  # tune if needed

# # Autoencoder anomaly margin: how far above T* we require to block
# AE_MSE_FACTOR = 1.30  # 1.3x T*; increase to reduce false positives further

# try:
#     # Load Models
#     model_clf = tf.keras.models.load_model(MODEL_PATH)
#     autoencoder = tf.keras.models.load_model(AE_MODEL_PATH)

#     # Load Preprocessing Assets
#     with open(ASSETS_PATH, 'rb') as f:
#         assets = pickle.load(f)

#     scaler_fit = assets['scaler']
#     feature_names = assets['feature_names']  # full feature space (e.g., 119)
#     adaptive_threshold = assets['adaptive_threshold']  # baseline AE threshold from Colab

#     # Baseline threshold used before game-theoretic adjustment
#     T_normal_baseline = adaptive_threshold

#     # --- Get the TRUE number of input features from the models (should be 119) ---
#     n_model_features_clf = model_clf.input_shape[-1]
#     n_model_features_ae = autoencoder.input_shape[-1]

#     if n_model_features_clf != n_model_features_ae:
#         print(
#             f"WARNING: Classifier expects {n_model_features_clf} features, "
#             f"autoencoder expects {n_model_features_ae} features."
#         )

#     # Use classifier input size as canonical
#     N_FEATURES = n_model_features_clf
#     print(f"Model input dimension (N_FEATURES) = {N_FEATURES}")

#     # Optional: print scaler expected features (likely 38 in your case)
#     if hasattr(scaler_fit, "n_features_in_"):
#         print(f"Scaler expects {scaler_fit.n_features_in_} features as input")
#     else:
#         print("Scaler has no n_features_in_ attribute; will treat as generic transformer.")

#     # Optional: disable strict feature-name checking; we use raw NumPy arrays
#     try:
#         if hasattr(scaler_fit, "feature_names_in_"):
#             del scaler_fit.feature_names_in_
#     except Exception as e:
#         print(f"Warning: could not remove feature_names_in_ from scaler: {e}")

#     print("--- Models and Assets Loaded Successfully ---")

# except Exception as e:
#     print(f"CRITICAL ERROR: Could not load one or more assets: {e}")
#     exit(1)


# # --- FEATURE EXTRACTION (Now attempting to process request data) ---
# def extract_and_process_features(request_obj):
#     payload = request_obj.form.get('payload', '').strip().lower()
#     url = request_obj.url.lower()
#     method = request_obj.method  # reserved for future use (e.g., mapping HTTP method)

#     # Create base numeric feature vector with the EXACT size required by the models (e.g., 119)
#     feature_vector = np.zeros(N_FEATURES, dtype=np.float32)

#     # --- SIMULATED MAPPING TO FEATURES (MUST BE CUSTOMIZED FOR REAL ACCURACY) ---

#     # 1. Simulate Numeric Features
#     # Feature 0 (Proxy for size/count): Use payload length
#     if N_FEATURES > 0:
#         feature_vector[0] = min(len(payload) / 500.0, 5.0)

#     # Feature 1 (Proxy for Data Volume): Use URL length
#     if N_FEATURES > 1:
#         feature_vector[1] = min(len(url) / 50.0, 5.0)

#     # Feature 2 (Proxy for Time/Entropy): Use a time-based feature (simulated)
#     if N_FEATURES > 2:
#         feature_vector[2] = (time.time() % 100) / 100.0

#     # 2. Simulate Categorical / Indicator Features
#     # For known suspicious patterns (e.g., simple SQLi pattern)
#     if 'union select' in payload or 'or 1=1' in payload:
#         # Choose some stable indicator index within the available feature dimension
#         indicator_index = 100  # arbitrary but <= N_FEATURES-1
#         if N_FEATURES > indicator_index:
#             feature_vector[indicator_index] = 1.0

#     # --- END TEMPORARY MAPPING ---

#     # Reshape to (1, n_features) for scaler and models
#     feature_vector_2d = feature_vector.reshape(1, -1)

#     # Apply scaler ONLY if it is compatible with the model input dimension
#     use_scaler = hasattr(scaler_fit, "n_features_in_") and scaler_fit.n_features_in_ == N_FEATURES
#     if use_scaler:
#         X_scaled = scaler_fit.transform(feature_vector_2d)
#     else:
#         # For now, we skip scaling if incompatible (e.g., scaler was fit on 38 features only).
#         X_scaled = feature_vector_2d

#     # Crucial: Ensure the final vector is the correct type for Keras
#     return X_scaled.astype(np.float32)


# # --- NEW: Function to Solve the Game Based On an Attack Probability Vector ---
# def solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob):
#     """Calculates the optimal defender strategy (D*) based on assumed attack distribution."""
#     num_defender_actions = payoff_matrix.shape[1]
#     expected_defender_payoffs = np.zeros(num_defender_actions)

#     for j in range(num_defender_actions):
#         expected_payoff = np.dot(attack_distribution_prob, payoff_matrix[:, j])
#         expected_defender_payoffs[j] = expected_payoff

#     optimal_defender_strategy_index = np.argmax(expected_defender_payoffs)

#     # Map index (0 or 1) to the adaptive factor (D2 = 0.8, D1 = 1.2)
#     if optimal_defender_strategy_index == 1:  # D2 (Low Threshold/Aggressive)
#         adaptive_factor = 0.8
#     else:  # D1 (High Threshold/Conservative)
#         adaptive_factor = 1.2

#     return adaptive_factor, optimal_defender_strategy_index


# # --- SECURITY AGENT LOGIC (Module C guides B, A runs independently) ---
# def agentic_decision(feature_vector, payload):
#     # 1. MODULE A: Known Attack Detection (Keras Classifier)
#     prediction = model_clf.predict(feature_vector, verbose=0)[0]  # shape: (num_classes,)
#     predicted_class_index = int(np.argmax(prediction))
#     max_prob = float(np.max(prediction))

#     # Treat as "known attack" ONLY if:
#     #  - not class 0 (BENIGN / NORMAL)
#     #  - AND probability is high (>= CLF_ATTACK_PROB_THRESHOLD)
#     is_known_attack_high_conf = (predicted_class_index != 0) and (max_prob >= CLF_ATTACK_PROB_THRESHOLD)

#     # 2. MODULE B: Unknown Attack Detection (Autoencoder)
#     reconstruction = autoencoder.predict(feature_vector, verbose=0)
#     mse = float(np.mean(np.power(feature_vector - reconstruction, 2), axis=1)[0])

#     # 3. MODULE C: DYNAMIC Adaptive Threshold (The Agentic Part)
#     payoff_matrix = np.array([
#         [2, 5],
#         [4, 8]
#     ])  # Conceptual Payoff Matrix

#     # *** SIMULATION STEP ***: Agent assesses current threat landscape (e.g., 50/50 mix)
#     attack_distribution_prob = np.array([0.5, 0.5])
#     adaptive_factor, strategy_idx = solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob)

#     global T_normal_baseline
#     T_star_base = float(T_normal_baseline * adaptive_factor)
#     # Apply extra safety factor so AE only fires on *strong* anomalies
#     T_star_effective = T_star_base * AE_MSE_FACTOR
#     is_unknown_attack = mse > T_star_effective

#     # 4. Simple signature-based override for very obvious attacks
#     payload_lower = payload.lower()
#     is_signature_attack = any(
#         kw in payload_lower
#         for kw in [
#             "union select",
#             " or 1=1",
#             "' or '1'='1",
#             "\" or \"1\"=\"1",
#             "drop table",
#             "xp_cmdshell",
#         ]
#     )

#     # --- FINAL DECISION (Standard Flow) ---

#     if is_signature_attack:
#         return True, "BLOCKED", (
#             "Signature-based SQLi detection triggered. "
#             f"(payload matched known attack pattern; MSE={mse:.4f}, T*={T_star_effective:.4f})"
#         )

#     if is_known_attack_high_conf and is_unknown_attack:
#         return True, "BLOCKED", (
#             "High-confidence Known Attack + AE strong anomaly. "
#             f"(class={predicted_class_index}, prob={max_prob:.3f}, "
#             f"MSE={mse:.4f} > T*={T_star_effective:.4f})"
#         )

#     if is_known_attack_high_conf:
#         return True, "BLOCKED", (
#             "High-confidence Known Attack (Module A). "
#             f"(class={predicted_class_index}, prob={max_prob:.3f}, "
#             f"MSE={mse:.4f}, T*={T_star_effective:.4f})"
#         )

#     if is_unknown_attack:
#         return True, "BLOCKED", (
#             "Unknown Attack Detected (Module B - strong AE anomaly). "
#             f"(MSE={mse:.4f} > T*={T_star_effective:.4f}, classifier_class={predicted_class_index}, "
#             f"class_prob={max_prob:.3f})"
#         )

#     # Default: If neither high-confidence classifier nor AE triggers, allow access.
#     return False, "ALLOWED", (
#         f"Normal / Low-Risk Traffic. "
#         f"(class={predicted_class_index}, prob={max_prob:.3f}, "
#         f"MSE={mse:.4f}, T*={T_star_effective:.4f})"
#     )


# # --- WEB SERVER ROUTES ---
# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/submit_test', methods=['POST'])
# def submit_test():
#     try:
#         # CORE AGENT EXECUTION
#         feature_vector = extract_and_process_features(request)
#         payload = request.form.get('payload', '').strip()

#         is_blocked, status, reason = agentic_decision(feature_vector, payload)

#         if is_blocked:
#             return jsonify({"status": status, "reason": reason}), 403
#         else:
#             return jsonify({"status": status, "reason": reason}), 200

#     except Exception as e:
#         # Helpful debugging info in JSON
#         return jsonify({"status": "ERROR", "reason": str(e)}), 500


# if __name__ == '__main__':
#     # Run the Flask app
#     app.run(debug=True)


# app.py - The Agentic AI Intrusion Detection Server (FINAL REAL-TIME PROXY VERSION)

import pickle
import numpy as np
import tensorflow as tf
import pandas as pd  # kept for possible future uses (not critical now)
from flask import Flask, request, render_template, jsonify
import time  # Needed for time-based features

# --- GLOBAL VARIABLES & MODEL LOADING ---
app = Flask(__name__, template_folder='templates')
MODEL_PATH = 'model_classifier.keras'
AE_MODEL_PATH = 'model_autoencoder.keras'
ASSETS_PATH = 'preprocessing_assets.pkl'

# Classifier confidence threshold: only treat as "known attack" if probability is high
CLF_ATTACK_PROB_THRESHOLD = 0.80  # tune if needed

# Autoencoder anomaly margin: how far above T* we require to block
AE_MSE_FACTOR = 1.30  # 1.3x T*; increase to reduce false positives further


try:
    # Load Models
    model_clf = tf.keras.models.load_model(MODEL_PATH)
    autoencoder = tf.keras.models.load_model(AE_MODEL_PATH)

    # Load Preprocessing Assets
    with open(ASSETS_PATH, 'rb') as f:
        assets = pickle.load(f)

    scaler_fit = assets['scaler']
    feature_names = assets['feature_names']  # full feature space (e.g., 119)
    adaptive_threshold = assets['adaptive_threshold']  # baseline AE threshold from Colab

    # Baseline threshold used before game-theoretic adjustment
    T_normal_baseline = adaptive_threshold

    # --- Get the TRUE number of input features from the models (should be 119) ---
    n_model_features_clf = model_clf.input_shape[-1]
    n_model_features_ae = autoencoder.input_shape[-1]

    if n_model_features_clf != n_model_features_ae:
        print(
            f"WARNING: Classifier expects {n_model_features_clf} features, "
            f"autoencoder expects {n_model_features_ae} features."
        )

    # Use classifier input size as canonical
    N_FEATURES = n_model_features_clf
    print(f"Model input dimension (N_FEATURES) = {N_FEATURES}")

    # Optional: print scaler expected features (likely 38 in your case)
    if hasattr(scaler_fit, "n_features_in_"):
        print(f"Scaler expects {scaler_fit.n_features_in_} features as input")
    else:
        print("Scaler has no n_features_in_ attribute; will treat as generic transformer.")

    # Optional: disable strict feature-name checking; we use raw NumPy arrays
    try:
        if hasattr(scaler_fit, "feature_names_in_"):
            del scaler_fit.feature_names_in_
    except Exception as e:
        print(f"Warning: could not remove feature_names_in_ from scaler: {e}")

    print("--- Models and Assets Loaded Successfully ---")

except Exception as e:
    print(f"CRITICAL ERROR: Could not load one or more assets: {e}")
    exit(1)


# --- PAYLOAD PATTERN ANALYZER (Module 0) ---
def detect_attack_categories(payload_raw: str):
    """
    Analyze the raw payload string and dynamically classify it into high-level
    web attack families: SQLi, XSS, Command Injection, Path Traversal, Fuzzing.
    Returns:
        categories: list[str] (e.g. ["SQLi", "XSS"])
        risk_score: int (number of categories matched; simple measure)
    """
    payload = payload_raw.lower()
    categories = []

    # --- SQL Injection–style detection ---
    sqli_keywords = [
        "union select",
        " or 1=1",
        "or 1=1",
        "' or '1'='1",
        "\" or \"1\"=\"1",
        "admin'--",
        "admin' or",
        "admin\" or",
        "drop table",
        "insert into",
        "update ",
        "delete from",
        "where 1=1",
        "--",
        ";--",
        "/*",
        "*/",
    ]
    if any(kw in payload for kw in sqli_keywords):
        categories.append("SQL Injection–style")

    # --- XSS (Cross-Site Scripting)–style detection ---
    xss_keywords = [
        "<script",
        "</script",
        "onerror=",
        "onload=",
        "onclick=",
        "onmouseover=",
        "javascript:",
        "alert(",
        "<img",
        "<svg",
        "<iframe",
    ]
    if any(kw in payload for kw in xss_keywords):
        categories.append("XSS (Cross-Site Scripting)–style")

    # --- Command Injection–style detection ---
    cmd_meta_chars = ["&&", "||", ";", "|", "`", "$("]
    cmd_keywords = [
        "rm -rf",
        "cat /etc/passwd",
        "wget ",
        "curl ",
        "nc ",
        "bash",
        "sh ",
        "powershell",
        "cmd.exe",
        "net user",
    ]
    if any(mc in payload for mc in cmd_meta_chars) and any(
        ck in payload for ck in cmd_keywords
    ):
        categories.append("Command Injection–style")

    # --- Path Traversal–style detection ---
    traversal_keywords = [
        "../",
        "..\\",
        "%2e%2e%2f",  # URL-encoded ../
        "/etc/passwd",
        "boot.ini",
        "windows/system32",
        "..%2f",
        "..%5c",
    ]
    if any(kw in payload for kw in traversal_keywords):
        categories.append("Path Traversal–style")

    # --- Miscellaneous fuzzing / anomaly detection ---
    # Heuristics: long length, high repetition, lots of non-alphanumeric
    length = len(payload_raw)
    if length > 0:
        # character frequency
        from collections import Counter

        counts = Counter(payload_raw)
        max_freq = max(counts.values()) / float(length)
        non_alnum_ratio = sum(not c.isalnum() and not c.isspace() for c in payload_raw) / float(length)

        fuzz_like = (
            length > 200  # very long input
            or max_freq > 0.6  # same char repeated a lot, like "AAAAAA..." or "!!!!!"
            or non_alnum_ratio > 0.6  # mostly symbols
        )
        if fuzz_like:
            categories.append("Fuzzing / Anomalous Input–style")

    risk_score = len(categories)
    return categories, risk_score


# --- FEATURE EXTRACTION (Now attempting to process request data) ---
def extract_and_process_features(request_obj):
    payload = request_obj.form.get('payload', '').strip().lower()
    url = request_obj.url.lower()
    method = request_obj.method  # reserved for future use (e.g., mapping HTTP method)

    # Create base numeric feature vector with the EXACT size required by the models (e.g., 119)
    feature_vector = np.zeros(N_FEATURES, dtype=np.float32)

    # --- SIMULATED MAPPING TO FEATURES (MUST BE CUSTOMIZED FOR REAL ACCURACY) ---

    # 1. Simulate Numeric Features
    # Feature 0 (Proxy for size/count): Use payload length
    if N_FEATURES > 0:
        feature_vector[0] = min(len(payload) / 500.0, 5.0)

    # Feature 1 (Proxy for Data Volume): Use URL length
    if N_FEATURES > 1:
        feature_vector[1] = min(len(url) / 50.0, 5.0)

    # Feature 2 (Proxy for Time/Entropy): Use a time-based feature (simulated)
    if N_FEATURES > 2:
        feature_vector[2] = (time.time() % 100) / 100.0

    # 2. Simulate Categorical / Indicator Features (basic)
    if 'union select' in payload or 'or 1=1' in payload:
        indicator_index = 100  # arbitrary but within N_FEATURES
        if N_FEATURES > indicator_index:
            feature_vector[indicator_index] = 1.0

    # --- END TEMPORARY MAPPING ---

    # Reshape to (1, n_features) for scaler and models
    feature_vector_2d = feature_vector.reshape(1, -1)

    # Apply scaler ONLY if it is compatible with the model input dimension
    use_scaler = hasattr(scaler_fit, "n_features_in_") and scaler_fit.n_features_in_ == N_FEATURES
    if use_scaler:
        X_scaled = scaler_fit.transform(feature_vector_2d)
    else:
        X_scaled = feature_vector_2d

    # Crucial: Ensure the final vector is the correct type for Keras
    return X_scaled.astype(np.float32)


# --- NEW: Function to Solve the Game Based On an Attack Probability Vector ---
def solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob):
    """Calculates the optimal defender strategy (D*) based on assumed attack distribution."""
    num_defender_actions = payoff_matrix.shape[1]
    expected_defender_payoffs = np.zeros(num_defender_actions)

    for j in range(num_defender_actions):
        expected_payoff = np.dot(attack_distribution_prob, payoff_matrix[:, j])
        expected_defender_payoffs[j] = expected_payoff

    optimal_defender_strategy_index = np.argmax(expected_defender_payoffs)

    # Map index (0 or 1) to the adaptive factor (D2 = 0.8, D1 = 1.2)
    if optimal_defender_strategy_index == 1:  # D2 (Low Threshold/Aggressive)
        adaptive_factor = 0.8
    else:  # D1 (High Threshold/Conservative)
        adaptive_factor = 1.2

    return adaptive_factor, optimal_defender_strategy_index


# --- SECURITY AGENT LOGIC (Module C guides B, A runs independently) ---
def agentic_decision(feature_vector, payload_raw):
    # 0. MODULE 0: Pattern-based Web Attack Categorizer
    categories, pattern_risk = detect_attack_categories(payload_raw)

    # 1. MODULE A: Known Attack Detection (Keras Classifier)
    prediction = model_clf.predict(feature_vector, verbose=0)[0]  # shape: (num_classes,)
    predicted_class_index = int(np.argmax(prediction))
    max_prob = float(np.max(prediction))

    is_known_attack_high_conf = (predicted_class_index != 0) and (max_prob >= CLF_ATTACK_PROB_THRESHOLD)

    # 2. MODULE B: Unknown Attack Detection (Autoencoder)
    reconstruction = autoencoder.predict(feature_vector, verbose=0)
    mse = float(np.mean(np.power(feature_vector - reconstruction, 2), axis=1)[0])

    # 3. MODULE C: DYNAMIC Adaptive Threshold (The Agentic Part)
    payoff_matrix = np.array([
        [2, 5],
        [4, 8]
    ])  # Conceptual Payoff Matrix

    # Example: treat environment as 50/50 mix of low/medium threat
    attack_distribution_prob = np.array([0.5, 0.5])
    adaptive_factor, strategy_idx = solve_game_for_optimal_strategy(payoff_matrix, attack_distribution_prob)

    global T_normal_baseline
    T_star_base = float(T_normal_baseline * adaptive_factor)
    T_star_effective = T_star_base * AE_MSE_FACTOR
    is_unknown_attack = mse > T_star_effective

    # --- FINAL DECISION LOGIC ---

    # A. Strong pattern detection -> immediate BLOCK with attack family labels
    if pattern_risk > 0:
        attack_label = ", ".join(categories)
        return True, "BLOCKED", (
            f"Rule-based Web Attack Detection: {attack_label}. "
            f"(MSE={mse:.4f}, T*={T_star_effective:.4f}, "
            f"class={predicted_class_index}, prob={max_prob:.3f})"
        )

    # B. Agentic combination: classifier + autoencoder
    if is_known_attack_high_conf and is_unknown_attack:
        return True, "BLOCKED", (
            "High-confidence Known Attack + AE strong anomaly. "
            f"(class={predicted_class_index}, prob={max_prob:.3f}, "
            f"MSE={mse:.4f} > T*={T_star_effective:.4f})"
        )

    if is_known_attack_high_conf:
        return True, "BLOCKED", (
            "High-confidence Known Attack (Module A). "
            f"(class={predicted_class_index}, prob={max_prob:.3f}, "
            f"MSE={mse:.4f}, T*={T_star_effective:.4f})"
        )

    if is_unknown_attack:
        return True, "BLOCKED", (
            "Unknown Attack Detected (Module B - strong AE anomaly). "
            f"(MSE={mse:.4f} > T*={T_star_effective:.4f}, "
            f"class={predicted_class_index}, prob={max_prob:.3f})"
        )

    # C. Otherwise: allow
    return False, "ALLOWED", (
        "Normal / Low-Risk Traffic. "
        f"(class={predicted_class_index}, prob={max_prob:.3f}, "
        f"MSE={mse:.4f}, T*={T_star_effective:.4f})"
    )


# --- WEB SERVER ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit_test', methods=['POST'])
def submit_test():
    try:
        # CORE AGENT EXECUTION
        feature_vector = extract_and_process_features(request)
        payload = request.form.get('payload', '').strip()

        is_blocked, status, reason = agentic_decision(feature_vector, payload)

        if is_blocked:
            return jsonify({"status": status, "reason": reason}), 403
        else:
            return jsonify({"status": status, "reason": reason}), 200

    except Exception as e:
        # Helpful debugging info in JSON
        return jsonify({"status": "ERROR", "reason": str(e)}), 500


if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
