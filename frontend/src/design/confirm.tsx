import {
  useEffect,
  useState,
} from "react";
import { Button } from "./primitives";
import { t } from "../i18n/de";
import "./confirm.css";

interface ConfirmOptions {
  title?: string;
  confirmLabel?: string;
  cancelLabel?: string;
}

interface ConfirmRequest extends ConfirmOptions {
  message: string;
  resolve: (value: boolean) => void;
}

const queue: ConfirmRequest[] = [];

let wake:
  | (() => void)
  | null = null;

/**
 * Öffnet eine Bestätigung innerhalb von Kehler OS.
 *
 * Anders als window.confirm gehört dieser Dialog zur Oberfläche selbst.
 * Dadurch sieht und funktioniert er auf Handy, Tablet, Desktop und dem
 * eingebetteten Siemens-HMI identisch.
 */
export function confirmInApp(
  message: string,
  options: ConfirmOptions = {},
): Promise<boolean> {
  return new Promise((resolve) => {
    queue.push({
      message,
      resolve,
      ...options,
    });

    wake?.();
  });
}

export function ConfirmationHost() {
  const [current, setCurrent] =
    useState<ConfirmRequest | null>(null);

  useEffect(() => {
    function showNext() {
      setCurrent((existing) => {
        if (existing !== null) {
          return existing;
        }

        return queue.shift() ?? null;
      });
    }

    wake = showNext;
    showNext();

    return () => {
      if (wake === showNext) {
        wake = null;
      }
    };
  }, []);

  useEffect(() => {
    if (current === null) {
      wake?.();
      return;
    }

    function keyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        finish(false);
      }
    }

    window.addEventListener(
      "keydown",
      keyDown,
    );

    return () =>
      window.removeEventListener(
        "keydown",
        keyDown,
      );
  }, [current]);

  function finish(answer: boolean) {
    if (current === null) {
      return;
    }

    const request = current;

    setCurrent(null);
    request.resolve(answer);
  }

  if (current === null) {
    return null;
  }

  return (
    <div
      className="confirm-overlay"
      role="presentation"
      onPointerDown={(event) => {
        if (
          event.target ===
          event.currentTarget
        ) {
          finish(false);
        }
      }}
    >
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby="confirm-message"
      >
        <div className="confirm-dialog__mark">
          !
        </div>

        <div className="confirm-dialog__content">
          <h2
            id="confirm-title"
            className="confirm-dialog__title"
          >
            {current.title ??
              t("confirm.title")}
          </h2>

          <p
            id="confirm-message"
            className="confirm-dialog__message"
          >
            {current.message}
          </p>
        </div>

        <div className="confirm-dialog__actions">
          <Button
            onClick={() => finish(false)}
          >
            {current.cancelLabel ??
              t("confirm.cancel")}
          </Button>

          <Button
            variant="accent"
            onClick={() => finish(true)}
          >
            {current.confirmLabel ??
              t("confirm.accept")}
          </Button>
        </div>
      </section>
    </div>
  );
}
