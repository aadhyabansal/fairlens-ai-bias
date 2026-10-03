import { createContext, useContext, useState } from 'react';

const AuditContext = createContext(null);

export function AuditProvider({ children }) {
  const [currentAudit, setCurrentAudit] = useState(null);
  const [currentMitigation, setCurrentMitigation] = useState(null);
  const [currentReport, setCurrentReport] = useState(null);

  return (
    <AuditContext.Provider
      value={{
        currentAudit, setCurrentAudit,
        currentMitigation, setCurrentMitigation,
        currentReport, setCurrentReport,
      }}
    >
      {children}
    </AuditContext.Provider>
  );
}

export function useAudit() {
  return useContext(AuditContext);
}