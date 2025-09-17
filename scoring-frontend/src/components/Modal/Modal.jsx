import "./Modal.css";

export default function Modal({ children }) {
  return (
    <div className="modal-bg">
      <div className="modal-content">{children}</div>
    </div>
  );
}
