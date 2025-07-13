import { useEffect, useState } from "react";
import TwoColumnLayout from "../../components/TwoColumnLayout/TwoColumnLayout";
import ExcelExportSelector from "./Components/ExcelExportSelector";
import PlusMinus from "./Components/PlusMinus";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function ExcelExporter() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [games, setGames] = useState([]);

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
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

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

  const downloadGames = async () => {
    const token = sessionStorage.getItem("jwt_token");
    try {
      const response = await fetch(`${BACKEND_URL}/games/get-for-user`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.log("Error in downlaodGames");
        return;
      }

      const data = await response.json();
      console.log(data);
      setGames(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    downloadGames();
  }, []);

  return (
    <TwoColumnLayout
      left={
        <ExcelExportSelector
          selectedId={selectedReport}
          onSelect={setSelectedReport}
        ></ExcelExportSelector>
      }
      right={
        <>
          <div>
            {selectedReport ? (
              <p></p>
            ) : (
              <p>Valitse vasemmalta raportti jatkaaksesi</p>
            )}
          </div>

          {selectedReport === "plusminus" ? (
            <PlusMinus games={games}></PlusMinus>
          ) : selectedReport === "team" ? (
            <p>SHOW TEAM</p>
          ) : selectedReport === "goalies" ? (
            <p>SHOW GOALIES</p>
          ) : (
            <p></p>
          )}

          {/* <div>
            <button onClick={downloadExcel}>Download test</button>
            <button onClick={downloadTeamStats}>Download team stats</button>
            <button onClick={downloadPlusMinus}>Download plusminus</button>
          </div> */}
        </>
      }
    ></TwoColumnLayout>
  );
}
