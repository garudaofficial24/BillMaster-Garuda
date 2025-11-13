import React, { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

/**
 * SafeSelect - A wrapper around Shadcn Select that handles undefined/null values safely
 * Prevents "Cannot read properties of undefined (reading 'getBoundingClientRect')" errors
 */
export const SafeSelect = ({ value, onValueChange, children, defaultValue, ...props }) => {
  // Ensure value is always defined for controlled component
  const [internalValue, setInternalValue] = useState(value || defaultValue || "");
  
  useEffect(() => {
    // Sync internal value with external value when it changes
    if (value !== undefined && value !== null) {
      setInternalValue(value);
    } else if (defaultValue) {
      setInternalValue(defaultValue);
    }
  }, [value, defaultValue]);
  
  const handleValueChange = (newValue) => {
    setInternalValue(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
  };
  
  return (
    <Select 
      value={internalValue || defaultValue || undefined} 
      onValueChange={handleValueChange}
      {...props}
    >
      {children}
    </Select>
  );
};

export { SelectContent, SelectItem, SelectTrigger, SelectValue };
