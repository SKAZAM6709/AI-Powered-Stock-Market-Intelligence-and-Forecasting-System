import numpy as np

from keras.models import Sequential

from keras.layers import (
    LSTM,
    Dense,
    Dropout,
)

from keras.callbacks import (
    EarlyStopping,
)


def create_sequences(
    data,
    sequence_length: int = 60
):
    """
    Convert stock-price data into sequences
    suitable for an LSTM model.

    Previous sequence_length prices
    are used to predict the next price.
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
            "Not enough data to create LSTM sequences."
        )

    X = X.reshape(
        X.shape[0],
        X.shape[1],
        1
    )

    return X, y


def create_lstm_model(
    sequence_length: int = 60
):
    """
    Create an LSTM model for
    next-day stock-price prediction.
    """

    model = Sequential()

    model.add(
        LSTM(
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
        LSTM(
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
        metrics=[
            "mae"
        ]
    )

    return model


def train_lstm_model(
    model,
    X_train,
    y_train,
    X_validation=None,
    y_validation=None,
    epochs: int = 30,
    batch_size: int = 32
):
    """
    Train the LSTM model with
    early stopping.
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