import { useEffect, useState } from "react";
import TwoColumnLayout from "../../components/TwoColumnLayout/TwoColumnLayout";
import ExcelExportSelector from "./Components/ExcelExportSelector";
import GamesSelector from "./Components/GamesSelector";
import GamesSelector from "./Components/GamesSelector";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export default function ExcelExporter() {
  const [selectedReport, setSelectedReport] = useState(null);
  const [games, setGames] = useState([]);

  const downloadExcel = async () => {
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
            <GamesSelector
              games={games}
              reportDownloadEndpoint="plusminus"
            ></GamesSelector>
            <GamesSelector
              games={games}
              reportDownloadEndpoint="plusminus"
            ></GamesSelector>
          ) : selectedReport === "team" ? (
            <GamesSelector
              games={games}
              reportDownloadEndpoint="teamstats"
            ></GamesSelector>
          ) : selectedReport === "games" ? (
            <GamesSelector
              games={games}
              reportDownloadEndpoint="game-stats"
            ></GamesSelector>
          ) : selectedReport === "playersSummary" ? (
            <GamesSelector
              games={games}
              reportDownloadEndpoint="player-stats"
            ></GamesSelector>
          ) : selectedReport === "goalies" ? (
            <p>SHOW GOALIES</p>
          ) : (
            <p></p>
          )}
        </>
      }
    ></TwoColumnLayout>
  );
}
