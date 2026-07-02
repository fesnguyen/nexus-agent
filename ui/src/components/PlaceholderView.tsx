export default function PlaceholderView({ label }) {
  return (
    <div className="flex h-full items-center justify-center">
      <div className="text-center">
        <h2 className="text-lg font-semibold text-ink">{label}</h2>
        <p className="mt-1 text-sm text-muted">Coming soon</p>
      </div>
    </div>
  );
}
