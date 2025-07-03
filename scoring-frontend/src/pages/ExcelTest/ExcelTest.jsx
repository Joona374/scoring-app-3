const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function ExcelTest() {
  const downloadExcel = async () => {
    console.log("This should dl");
    const res = await fetch(`${BACKEND_URL}/excel/download-test`);
    const fileBlob = await res.blob();
    const tempUrl = URL.createObjectURL(fileBlob);
    const aElement = document.createElement("a");
    aElement.href = tempUrl;
    aElement.download = "stats.xlsx";
    aElement.click();
  };
  return <button onClick={downloadExcel}>Download</button>;
}
