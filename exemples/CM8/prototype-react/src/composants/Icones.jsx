const attributsSvg = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true",
  focusable: "false",
};

export function IconeMenu(props) {
  return (
    <svg {...attributsSvg} width="22" height="22" {...props}>
      <path d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

export function IconeUtilisateur(props) {
  return (
    <svg {...attributsSvg} width="18" height="18" {...props}>
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5.2 20c1.3-3.2 3.8-4.8 6.8-4.8s5.5 1.6 6.8 4.8" />
    </svg>
  );
}

export function IconeChevron({ direction = "droite", style, ...props }) {
  const rotations = {
    droite: 0,
    bas: 90,
    gauche: 180,
    haut: -90,
  };

  return (
    <svg
      {...attributsSvg}
      width="18"
      height="18"
      {...props}
      style={{ rotate: `${rotations[direction] ?? 0}deg`, ...style }}
    >
      <path d="m9 6 6 6-6 6" />
    </svg>
  );
}

export function IconeDocument(props) {
  return (
    <svg {...attributsSvg} width="20" height="20" {...props}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5M9 13h6M9 17h4" />
    </svg>
  );
}

export function IconeCorbeille(props) {
  return (
    <svg {...attributsSvg} width="18" height="18" {...props}>
      <path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3" />
    </svg>
  );
}

export function IconePlus(props) {
  return (
    <svg {...attributsSvg} width="18" height="18" {...props}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  );
}

export function IconeFermer(props) {
  return (
    <svg {...attributsSvg} width="18" height="18" {...props}>
      <path d="m6 6 12 12M18 6 6 18" />
    </svg>
  );
}

export function IconeComptes(props) {
  return (
    <svg {...attributsSvg} width="19" height="19" {...props}>
      <path d="M13 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9z" />
      <path d="M13 3v6h6M9 13h6M9 17h4" />
    </svg>
  );
}

export function IconeTelechargement(props) {
  return (
    <svg {...attributsSvg} width="24" height="24" {...props}>
      <path d="M12 3v12M7 10l5 5 5-5M4 20h16" />
    </svg>
  );
}
