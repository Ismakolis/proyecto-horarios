/**
 * ConfirmModal.jsx
 * Modal de confirmacion reutilizable — reemplaza window.confirm()
 * 
 * Props:
 *   open      {boolean}   — si el modal esta visible
 *   title     {string}    — titulo del modal
 *   message   {string}    — mensaje descriptivo
 *   onConfirm {function}  — callback al confirmar
 *   onCancel  {function}  — callback al cancelar
 *   danger    {boolean}   — si true, boton de confirmar usa estilo peligro (rojo)
 *   loading   {boolean}   — muestra spinner en el boton confirmar
 *   confirmLabel {string} — texto del boton confirmar (default: "Confirmar")
 *   cancelLabel  {string} — texto del boton cancelar (default: "Cancelar")
 */
export default function ConfirmModal({
  open,
  title = 'Confirmar accion',
  message,
  onConfirm,
  onCancel,
  danger = true,
  loading = false,
  confirmLabel = 'Confirmar',
  cancelLabel  = 'Cancelar',
}) {
  if (!open) return null

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div
        className="modal"
        style={{ maxWidth: 420 }}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {/* Icono de advertencia */}
            <div style={{
              width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
              background: danger ? 'var(--brand-soft)' : 'var(--amber-soft)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                stroke={danger ? 'var(--brand)' : 'var(--amber)'}
                strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <h2>{title}</h2>
          </div>
          <button className="modal-close" onClick={onCancel} aria-label="Cerrar">×</button>
        </div>

        {message && (
          <p style={{
            fontSize: 13.5, color: 'var(--text-secondary)',
            lineHeight: 1.6, margin: '4px 0 4px',
          }}>
            {message}
          </p>
        )}

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </button>
          <button
            className={`btn ${danger ? 'btn-primary' : 'btn-success'}`}
            onClick={onConfirm}
            disabled={loading}
            style={danger ? { background: 'var(--brand)', borderColor: 'var(--brand)' } : {}}
          >
            {loading && (
              <span style={{
                width: 12, height: 12, borderRadius: '50%',
                border: '2px solid rgba(255,255,255,0.4)',
                borderTopColor: '#fff',
                display: 'inline-block',
                animation: 'spin 0.7s linear infinite',
                flexShrink: 0,
              }} />
            )}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
