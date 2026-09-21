from app.ui import ChessReaderUI
from core.controller import AppController


def main():
    controller = None

    def create_app():
        nonlocal controller

        controller = AppController(ui)

        ui.root.after(
            100,
            controller.start,
        )

    def close_app():
        if controller:
            controller.stop()

        ui.root.destroy()

    ui = ChessReaderUI(
        on_mode_change=lambda mode: (
            controller.set_mode(mode)
            if controller
            else None
        ),
        on_close=close_app,
    )

    create_app()

    ui.run()


if __name__ == "__main__":
    main()