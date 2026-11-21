export default function Chargement() {
  return (
    <div className="chargement" aria-busy="true" aria-live="polite">
      <span className="sr-only">Chargement des relevés…</span>
      <div className="squelette squelette--annee" />
      <div className="squelette squelette--annee" />
      <div className="squelette squelette--panneau">
        <div className="squelette squelette--entete" />
        <div className="squelette squelette--ligne" />
        <div className="squelette squelette--ligne" />
        <div className="squelette squelette--ligne" />
      </div>
    </div>
  );
}
