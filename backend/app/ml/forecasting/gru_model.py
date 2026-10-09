import numpy as np

from keras.models import Sequential
from keras.layers import (
    GRU,
    Dense,
    Dropout,
)
from keras.callbacks import EarlyStopping


def create_sequences(
    data,
    sequence_length: int = 60
):
    """
    Convert price data into GRU sequences.

    Previous 60 prices -> next price.
    """

    X = []
    y = []

    for i in range(
        sequence_length,
        len(data)
    ):
        X.append(
            data[
                i - sequence_length:i
            ]
        )

        y.append(
            data[i]
        )

    X = np.array(
        X,
        dtype=np.float32
    )

    y = np.array(
        y,
        dtype=np.float32
    )

    if len(X) == 0:
        raise ValueError(
            "Not enough data to create GRU sequences."
        )

    X = X.reshape(
        X.shape[0],
        X.shape[1],
        1
    )

    return X, y


def create_gru_model(
    sequence_length: int = 60
):
    """
    Create a GRU neural network for
    next-day stock-price prediction.
    """

    model = Sequential()

    model.add(
        GRU(
            units=64,
            return_sequences=True,
            input_shape=(
                sequence_length,
                1
            )
        )
    )

    model.add(
        Dropout(
            0.2
        )
    )

    model.add(
        GRU(
            units=32,
            return_sequences=False
        )
    )

    model.add(
        Dropout(
            0.2
        )
    )

    model.add(
        Dense(
            units=16,
            activation="relu"
        )
    )

    model.add(
        Dense(
            units=1
        )
    )

    model.compile(
        optimizer="adam",
        loss="mean_squared_error",
        metrics=["mae"]
    )

    return model


def train_gru_model(
    model,
    X_train,
    y_train,
    X_validation=None,
    y_validation=None,
    epochs: int = 30,
    batch_size: int = 32
):
    """
    Train GRU using early stopping.
    """

    monitor_value = (
        "val_loss"
        if (
            X_validation is not None
            and y_validation is not None
        )
        else "loss"
    )

    early_stopping = EarlyStopping(
        monitor=monitor_value,
        patience=5,
        restore_best_weights=True
    )

    validation_data = None

    if (
        X_validation is not None
        and y_validation is not None
    ):
        validation_data = (
            X_validation,
            y_validation
        )

    history = model.fit(
        X_train,
        y_train,
        validation_data=validation_data,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[
            early_stopping
        ],
        verbose=1,
        shuffle=False
    )

    return history