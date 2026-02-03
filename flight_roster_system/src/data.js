// src/data.js

export const MOCK_FLIGHTS = [
  { id: 'TK1234', route: 'ISTANBUL - ANKARA', date: '11.01.2026 - 17.51', planeType: 'Boeing 737', passengers: 123, crew: 12, source: 'Istanbul', destination: 'Ankara' },
  { id: 'BA456', route: 'ISTANBUL - LONDON', date: '12.01.2026 - 08.30', planeType: 'Airbus A320', passengers: 150, crew: 10, source: 'Istanbul', destination: 'London' },
  { id: 'TK789', route: 'IZMIR - ISTANBUL', date: '13.01.2026 - 14.20', planeType: 'Boeing 737', passengers: 110, crew: 12, source: 'Izmir', destination: 'Istanbul' },
  { id: 'LH101', route: 'MUNICH - ISTANBUL', date: '14.01.2026 - 09.15', planeType: 'Boeing 777', passengers: 280, crew: 16, source: 'Munich', destination: 'Istanbul' },
  { id: 'TK999', route: 'ANTALYA - MOSCOW', date: '15.01.2026 - 22.45', planeType: 'Airbus A330', passengers: 200, crew: 14, source: 'Antalya', destination: 'Moscow' },
];

export const MOCK_SAVED_ROSTERS = [
  { id: 'RST-001', flightId: 'TK1234', dateSaved: '10.01.2026 14:30', dbType: 'SQL ' },
  { id: 'RST-002', flightId: 'BA456', dateSaved: '10.01.2026 09:15', dbType: 'SQL ' },
  { id: 'RST-003', flightId: 'LH101', dateSaved: '09.01.2026 18:45', dbType: 'SQL ' },
  { id: 'RST-004', flightId: 'TK999', dateSaved: '08.01.2026 11:20', dbType: 'SQL ' },
];