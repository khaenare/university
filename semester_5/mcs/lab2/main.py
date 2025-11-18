import numpy as np
import time
import os
import matplotlib.pyplot as plt
from image_io import read_grayscale_image, save_grayscale_image
from pseudoinverse import (
    moore_penrose_pseudo_inverse,
    greville_pseudo_inverse,
    check_moore_penrose_conditions,
)


def add_bias_row(X: np.ndarray) -> np.ndarray:
    """
    Adds a row of ones at the bottom of the matrix X
    This helps to include a bias term in the linear transformation.
    """
    ones_row = np.ones((1, X.shape[1]), dtype=float)
    return np.vstack([X, ones_row])


def calculate_errors(true_values: np.ndarray, predicted_values: np.ndarray):
    """
    Computes the error metrics:
    - L1 norm
    - Mean Squared Error (MSE)
    - Root Mean Squared Error (RMSE)
    """
    residuals = true_values - predicted_values
    error_norm = np.linalg.norm(residuals, ord=1)
    mse = np.mean(residuals ** 2)
    rmse = np.sqrt(mse)
    return error_norm, mse, rmse


def construct_operator_and_predict(X: np.ndarray, Y: np.ndarray, pinv_func, method_name: str):
    """
    1) Augments the matrix X with a row of ones
    2) Computes the pseudo-inverse of the augmented matrix using the specified method
    3) Verifies the conditions of the Moore-Penrose pseudo-inverse
    4) Constructs the transformation matrix A
    5) Makes predictions and computes the errors
    """
    # Step 1: Augment the input matrix X with a row of ones
    X_augmented = add_bias_row(X)

    # Ensure the augmented matrix X has the correct dimensions
    print(f"X shape: {X.shape}, X_augmented shape: {X_augmented.shape}")

    # Step 2: Calculate the pseudo-inverse of the augmented matrix
    X_plus = pinv_func(X_augmented)

    # Step 3: Verify the Moore-Penrose conditions
    if not check_moore_penrose_conditions(X_augmented, X_plus):
        print(f"Warning: Moore-Penrose conditions failed for method: {method_name}")

    # Step 4: Construct matrix A
    A = Y @ X_plus

    # Step 5: Make predictions and calculate errors
    Y_pred = A @ X_augmented
    errors = calculate_errors(Y, Y_pred)

    print(f"Method: {method_name} - Errors: {errors}")
    return A, Y_pred, errors


def plot_comparison(results):
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Images
    axs[0, 0].imshow(results['X'], cmap='gray')
    axs[0, 0].set_title('Вхідне зображення X')

    axs[0, 1].imshow(results['Y'], cmap='gray')
    axs[0, 1].set_title('Цільове зображення Y')

    axs[1, 0].imshow(results['Y_pred_moore'], cmap='gray')
    axs[1, 0].set_title(f"Мур-Пенроуз\nRMSE = {results['RMSE_moore']}")

    axs[1, 1].imshow(results['Y_pred_greville'], cmap='gray')
    axs[1, 1].set_title(f"Гревіль\nRMSE = {results['RMSE_greville']}")

    plt.show()

    # Plot time comparison
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Мур-Пенроуз', 'Гревіль'], [results['time_moore'], results['time_greville']])
    ax.set_title('Час виконання')
    ax.set_ylabel('Час (секунди)')
    plt.show()

    # Plot RMSE comparison
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(['Мур-Пенроуз', 'Гревіль'], [results['RMSE_moore'], results['RMSE_greville']])
    ax.set_title('Похибка RMSE')
    ax.set_ylabel('RMSE')
    plt.show()

    # Display comparison table
    import pandas as pd
    comparison_data = {
        'Метод': ['Мур-Пенроуз', 'Гревіль'],
        'Час виконання (с)': [results['time_moore'], results['time_greville']],
        'RMSE': [results['RMSE_moore'], results['RMSE_greville']]
    }
    comparison_df = pd.DataFrame(comparison_data)
    print("\nТаблиця порівняння:")
    print(comparison_df)


def main():
    # 1. Load images and preprocess them
    X = read_grayscale_image('x3.bmp')
    Y = read_grayscale_image('y8.bmp')

    # 2. Augment X with a row of ones
    X_augmented = add_bias_row(X)

    # 3. Compute pseudo-inverse using both methods
    start_time = time.time()
    A_moore, Y_pred_moore, errors_moore = construct_operator_and_predict(X, Y, moore_penrose_pseudo_inverse,
                                                                         'Moore-Penrose')
    time_moore = time.time() - start_time
    print(f"Moore-Penrose execution time: {time_moore} seconds")

    start_time = time.time()
    A_greville, Y_pred_greville, errors_greville = construct_operator_and_predict(X, Y, greville_pseudo_inverse,
                                                                                  'Greville')
    time_greville = time.time() - start_time
    print(f"Greville execution time: {time_greville} seconds")

    # 4. Save the results
    save_grayscale_image('result_moore_penrose.bmp', Y_pred_moore)
    save_grayscale_image('result_greville.bmp', Y_pred_greville)

    # 5. Prepare comparison results
    results = {
        'X': X,
        'Y': Y,
        'Y_pred_moore': Y_pred_moore,
        'Y_pred_greville': Y_pred_greville,
        'RMSE_moore': errors_moore[2],
        'RMSE_greville': errors_greville[2],
        'time_moore': time_moore,
        'time_greville': time_greville
    }

    # 6. Visualize results and comparison
    plot_comparison(results)


if __name__ == "__main__":
    main()
