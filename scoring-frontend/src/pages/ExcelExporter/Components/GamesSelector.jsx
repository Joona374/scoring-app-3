import { useEffect, useState } from "react";
import "./GamesSelector.css";
import GameSelectorRow from "./GameSelectorRow";
import LoadingSpinner from "../../../components/LoadingSpinner/LoadingSpinner";

export default function GamesSelector({ games, reportDownloadEndpoint }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [homeAwayFilter, setHomeAwayFilter] = useState("");
  const [gamesSelected, setGamesSelected] = useState([]);
  const [filteredGames, setFilteredGames] = useState([]);
  const [sortColumn, setSortColumn] = useState("");
  const [sortDirection, setSortDirection] = useState("");
  const [isLoadingReport, setIsLoadingReport] = useState(false);

  const applyFilters = (filter, value) => {
    const dateFilteredGames = applyDateFilter(filter, value);
    const homeFilteredGames = filterHome(dateFilteredGames, filter, value);
    setFilteredGames(homeFilteredGames);
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

    return games;
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
    let direction;
    if (column === sortColumn && sortDirection === "ASC") {
      direction = "DESC";
    } else direction = "ASC";
    setSortDirection(direction);

    sortByColumn(column, direction);

    setSortColumn(column);
  };

  const sortByColumn = (column, direction) => {
    const newFilteredGames = [...filteredGames];
    newFilteredGames.sort((a, b) => {
      let sortedAttributeA;
      let sortedAttributeB;
      switch (column) {
        case "date":
          sortedAttributeA = new Date(a.date);
          sortedAttributeB = new Date(b.date);
          if (direction === "DESC") return sortedAttributeB - sortedAttributeA;
          else if (direction === "ASC")
            return sortedAttributeA - sortedAttributeB;
          break;

        case "opponent":
          sortedAttributeA = a.opponent;
          sortedAttributeB = b.opponent;
          if (direction === "DESC")
            return sortedAttributeB.localeCompare(sortedAttributeA);
          else if (direction === "ASC")
            return sortedAttributeA.localeCompare(sortedAttributeB);
          break;

        case "home":
          sortedAttributeA = a.home;
          sortedAttributeB = b.home;
          if (direction === "DESC") return sortedAttributeB - sortedAttributeA;
          else if (direction === "ASC")
            return sortedAttributeA - sortedAttributeB;
          break;

        default:
          console.error("ERROR IN SORTING BY COLUMN!");
          break;
      }
      console.log(sortedAttributeA, sortedAttributeB);
    });
    setFilteredGames(newFilteredGames);
  };

  const downloadReport = async () => {
    setIsLoadingReport(true);
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    try {
      const token = sessionStorage.getItem("jwt_token");
      const queryString = `game_ids=${gamesSelected.join(",")}`;
      const res = await fetch(
        `${BACKEND_URL}/excel/${reportDownloadEndpoint}?${queryString}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const fileBlob = await res.blob();
      const tempUrl = URL.createObjectURL(fileBlob);
      const aElement = document.createElement("a");
      aElement.href = tempUrl;
      aElement.download = "stats.xlsx";
      aElement.click();
      setIsLoadingReport(false);
    } catch {
      alert(
        "Virhe raporttia ladatessa. Yritä uudelleen tai ota yhteyttä ylläpitoon."
      );
      setIsLoadingReport(false);
    }
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
            <th className="games-sorting-th">Valittu</th>
            <th
              className={
                sortColumn === "date"
                  ? "active-sort games-sorting-th "
                  : "games-sorting-th "
              }
              onClick={() => handleSort("date")}
            >
              PVM{" "}
              {sortColumn === "date" && (
                <span>{sortDirection === "ASC" ? "▼" : "▲"}</span>
              )}
            </th>
            <th
              className={
                sortColumn === "opponent"
                  ? "active-sort games-sorting-th "
                  : "games-sorting-th "
              }
              onClick={() => handleSort("opponent")}
            >
              Vs{" "}
              {sortColumn === "opponent" && (
                <span>{sortDirection === "ASC" ? "▼" : "▲"}</span>
              )}
            </th>
            <th
              className={
                sortColumn === "home"
                  ? "active-sort games-sorting-th "
                  : "games-sorting-th "
              }
              onClick={() => handleSort("home")}
            >
              Koti/Vieras{" "}
              {sortColumn === "home" && (
                <span>{sortDirection === "ASC" ? "▲" : "▼"}</span>
              )}
            </th>
          </tr>
        </thead>
        <tbody>
          {filteredGames.map((game, idx) => {
            return (
              <GameSelectorRow
                game={game}
                key={idx}
                gamesSelected={gamesSelected}
                setGamesSelected={setGamesSelected}
              ></GameSelectorRow>
            );
          })}
        </tbody>
      </table>
      <div className="games-selector-excel-buttons">
        <div className="selection-controls">
          <button onClick={selectAll}>Valitse kaikki</button>
          <button onClick={resetSelection}>Nollaa valinta</button>
          <button onClick={downloadReport}>
            {isLoadingReport ? LoadingSpinner(15) : "Lataa raportti"}
          </button>
        </div>
      </div>
    </>
  );
}
