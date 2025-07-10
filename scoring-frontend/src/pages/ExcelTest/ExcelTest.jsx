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

  const downloadPlusMinus = async () => {
    console.log("This should plusminus");
    const token = sessionStorage.getItem("jwt_token");
    const res = await fetch(`${BACKEND_URL}/excel/plusminus`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const fileBlob = await res.blob();
    const tempUrl = URL.createObjectURL(fileBlob);
    const aElement = document.createElement("a");
    aElement.href = tempUrl;
    aElement.download = "stats.xlsx";
    aElement.click();
  };

  const downloadTeamStats = async () => {
    console.log("This should dl");
    const token = sessionStorage.getItem("jwt_token");
    try {
      const res = await fetch(`${BACKEND_URL}/excel/teamstats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const fileBlob = await res.blob();
      const tempUrl = URL.createObjectURL(fileBlob);
      const aElement = document.createElement("a");
      aElement.href = tempUrl;
      aElement.download = "teamstats.xlsx";
      aElement.click();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <button onClick={downloadExcel}>Download test</button>
      <button onClick={downloadTeamStats}>Download team stats</button>
      <button onClick={downloadPlusMinus}>Download plusminus</button>
    </div>
  );
}
