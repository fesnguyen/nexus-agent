export default function Logo({ size = 26 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="32" height="32" rx="9" fill="#5B4BDB" />
      <path
        d="M10 22V10.6c0-.5.62-.76.96-.4L21.4 21.6c.36.4.1.4-.4.4H10Z"
        fill="white"
      />
      <path d="M10 10h2.4v12H10z" fill="white" fillOpacity="0.95" />
      <circle cx="22" cy="10.4" r="1.6" fill="#C9BFFF" />
    </svg>
  );
}
