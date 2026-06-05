export function RecordList({ rows, emptyText }) {
  if (!rows.length) return <p>{emptyText}</p>;
  return (
    <div className="record-list">
      {rows.map((row) => (
        <div className="record-item" key={row.id}>
          <strong>{row.question || row.category_label || row.id}</strong>
          <small>{row.created_at}</small>
          <p>{row.comment || row.answer_mode || row.category_label || row.notice || ""}</p>
        </div>
      ))}
    </div>
  );
}
