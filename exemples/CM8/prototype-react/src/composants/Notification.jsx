import { IconeFermer } from "./Icones.jsx";

export default function Notification({ notification, onFermer, onAction }) {
  if (!notification) return null;

  return (
    <div className="notification" role="status" aria-live="polite">
      <span className="notification-message">{notification.message}</span>
      {notification.action ? (
        <button type="button" className="notification-action" onClick={onAction}>
          {notification.action.libelle}
        </button>
      ) : null}
      <button
        type="button"
        className="notification-fermer"
        aria-label="Fermer la notification"
        onClick={onFermer}
      >
        <IconeFermer />
      </button>
    </div>
  );
}
