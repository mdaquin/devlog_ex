import { useEffect, useRef } from "react";

/**
 * Ouvre et ferme un <dialog> natif (mode modal) en suivant l'état React.
 * Le navigateur gère alors le focus, la touche Échap et le fond assombri.
 */
export function useDialogue(ouverte) {
  const reference = useRef(null);

  useEffect(() => {
    const dialogue = reference.current;
    if (!dialogue) return undefined;

    if (ouverte && !dialogue.open) {
      dialogue.showModal();
    } else if (!ouverte && dialogue.open) {
      dialogue.close();
    }

    return () => {
      if (dialogue.open) dialogue.close();
    };
  }, [ouverte]);

  return reference;
}
