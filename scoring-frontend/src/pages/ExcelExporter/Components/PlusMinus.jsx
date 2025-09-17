import { useEffect, useState } from "react";
import "./PlusMinus.css";
import GameFilterSelector from "./GameFilterSelector";

export default function PlusMinus({ games }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [homeAwayFilter, setHomeAwayFilter] = useState("");
  const [gamesSelected, setGamesSelected] = useState([]);
  const [filteredGames, setFilteredGames] = useState([]);
  const [sortColumn, setSortColumn] = useState("");
  const [sortDirection, setSortDirection] = useState("");

  const applyFilters = (filter, value) => {
    const dateFilteredGames = applyDateFilter(filter, value);
    const homeFilteredGames = filterHome(dateFilteredGames, filter, value);
    setFilteredGames(homeFilteredGames);
  };

  const handleStartChange = (event) => {
    const startDate = event.target.value;
    apply("start", startDate);
  };

  const handleEndChange = (event) => {
    const endDate = event.target.value;
    applyDateFilter("end", endDate);
  };

  const applyDateFilter = (whichDate, dateString) => {
    let startDateObject;
    let endDateObject;

    if (whichDate == "start") {
      startDateObject = new Date(dateString);
      endDateObject = new Date(endDate);
      setStartDate(dateString);
    } else if (whichDate == "end") {
      startDateObject = new Date(startDate);
      endDateObject = new Date(dateString);
      setEndDate(dateString);
    } else if (whichDate === "reset") {
      startDateObject = new Date("01-01-1970");
      endDateObject = new Date("01-01-2070");
    } else {
      startDateObject = new Date(startDate);
      endDateObject = new Date(endDate);
    }

    if (isNaN(startDateObject.getTime())) {
      console.log("Invalid start");
      startDateObject = new Date("01-01-1970");
    }
    if (isNaN(endDateObject.getTime())) {
      console.log("Invalid end");
      endDateObject = new Date("01-01-2070");
    }

    console.log("start", startDateObject, "end", endDateObject);

    const gamesToShow = games.filter((game) => {
      const gameDateObject = new Date(game.date);
      return (
        gameDateObject >= startDateObject && gameDateObject <= endDateObject
      );
    });
    return gamesToShow;
  };

  const filterHome = (games, filter, value) => {
    let filterToUse;
    if (filter === "home") filterToUse = value;
    else filterToUse = homeAwayFilter;

    if (filterToUse === "BOTH") return games;
    else if (filterToUse === "HOME") {
      const gamesToShow = games.filter((game) => game.home === true);
      return gamesToShow;
    } else if (filterToUse === "AWAY") {
      const gamesToShow = games.filter((game) => game.home === false);
      return gamesToShow;
    }
  };

  const selectAll = () => {
    const allGameIds = filteredGames.map((game) => game.id);
    setGamesSelected(allGameIds);
  };

  const resetSelection = () => {
    setGamesSelected([]);
  };

  const resetDates = () => {
    setStartDate("");
    setEndDate("");
    applyFilters("reset", null);
  };

  const handleSort = (column) => {
    console.log("NEEDS TO BE IMPLEMENTED!!");
  };

  const downloadPlusMinus = async () => {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const token = sessionStorage.getItem("jwt_token");
    const queryString = `game_ids=${gamesSelected.join(",")}`;
    const res = await fetch(`${BACKEND_URL}/excel/plusminus?${queryString}`, {
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

  useEffect(() => {
    setFilteredGames(games);
  }, []);

  return (
    <>
      <div className="date-selectors">
        <div className="date-section">
          <label htmlFor="excel-start-date">Alkaen</label>
          <input
            type="date"
            id="excel-start-date"
            className="excel-date"
            value={startDate}
            onChange={() => applyFilters("start", event.target.value)}
          />
        </div>

        <div className="date-section">
          <label htmlFor="excel-end-date">Päättyen</label>
          <input
            type="date"
            id="excel-end-date"
            className="excel-date"
            value={endDate}
            onChange={() => applyFilters("end", event.target.value)}
          />
        </div>
        <button onClick={resetDates}>Nollaa</button>
      </div>

      <div className="game-location-radio">
        <label>
          <input
            type="radio"
            name="game-location"
            id="location-radio-BOTH"
            value="BOTH"
            checked={homeAwayFilter === "BOTH"}
            onChange={() => {
              setHomeAwayFilter("BOTH");
              applyFilters("home", "BOTH");
            }}
          />
          KAIKKI
        </label>
        <label>
          <input
            type="radio"
            name="game-location"
            id="location-radio-HOME"
            value="HOME"
            checked={homeAwayFilter === "HOME"}
            onChange={() => {
              setHomeAwayFilter("HOME");
              applyFilters("home", "HOME");
            }}
          />
          KOTI
        </label>
        <label>
          <input
            type="radio"
            name="game-location"
            id="location-radio-AWAY"
            value="AWAY"
            checked={homeAwayFilter === "AWAY"}
            onChange={() => {
              setHomeAwayFilter("AWAY");
              applyFilters("home", "AWAY");
            }}
          />
          VIERAS
        </label>
      </div>
      <table className="games-table">
        <thead>
          {/* TODO: IMPLEMENT SORTING */}
          <tr>
            <th onClick={() => handleSort("selected")}>Valittu</th>
            <th onClick={() => handleSort("date")}>PVM.</th>
            <th onClick={() => handleSort("opponent")}>Vs.</th>
            <th onClick={() => handleSort("home")}>Koti/Vieras</th>
          </tr>
        </thead>
        <tbody>
          {filteredGames.map((game, idx) => {
            return (
              <GameFilterSelector
                game={game}
                key={idx}
                gamesSelected={gamesSelected}
                setGamesSelected={setGamesSelected}
              ></GameFilterSelector>
            );
          })}
        </tbody>
      </table>
      <div className="plusminus-excel-buttons">
        <div className="selection-controls">
          <button onClick={selectAll}>Valitse kaikki</button>
          <button onClick={resetSelection}>Nollaa valinta</button>
          <button onClick={downloadPlusMinus}>Lataa raportti</button>
        </div>
      </div>
    </>
  );
}
