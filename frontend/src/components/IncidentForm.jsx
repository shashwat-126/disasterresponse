import React from "react";
import { useState } from "react";

const initialState = {
  title: "",
  description: "",
  disaster_type: "flood",
  location: "",
  latitude: "",
  longitude: "",
  people_affected: 0,
  injuries: 0,
  additional_info: "",
};

export default function IncidentForm({ onSubmit }) {
  const [form, setForm] = useState(initialState);
  const [files, setFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [locationError, setLocationError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: ["people_affected", "injuries", "latitude", "longitude"].includes(name)
        ? value === ""
          ? ""
          : Number(value)
        : value,
    }));
  }

  function updateField(name, value) {
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  async function detectLocation() {
    setLocationError("");

    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported in this browser.");
      return;
    }

    setLocating(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = Number(position.coords.latitude.toFixed(6));
        const lng = Number(position.coords.longitude.toFixed(6));

        updateField("latitude", lat);
        updateField("longitude", lng);
        updateField("location", `${lat}, ${lng}`);

        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`,
            {
              headers: {
                Accept: "application/json",
              },
            }
          );

          if (response.ok) {
            const data = await response.json();
            if (data?.display_name) {
              updateField("location", data.display_name);
            }
          }
        } catch (geoErr) {
          console.error("Reverse geocoding failed:", geoErr);
        } finally {
          setLocating(false);
        }
      },
      (geoError) => {
        setLocating(false);

        switch (geoError.code) {
          case 1:
            setLocationError("Location permission denied.");
            break;
          case 2:
            setLocationError("Location unavailable.");
            break;
          case 3:
            setLocationError("Location request timed out.");
            break;
          default:
            setLocationError("Failed to fetch your location.");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000,
      }
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await onSubmit(
        {
          ...form,
          latitude: form.latitude === "" ? null : form.latitude,
          longitude: form.longitude === "" ? null : form.longitude,
        },
        files
      );
      setForm(initialState);
      setFiles([]);
      setLocationError("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not submit incident.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Incident title</label>
        <input
          name="title"
          placeholder="Flood near Hebbal flyover"
          value={form.title}
          onChange={handleChange}
          required
        />
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Description</label>
        <textarea
          name="description"
          rows="4"
          placeholder="Describe the scale, visible damage, and immediate needs"
          value={form.description}
          onChange={handleChange}
          required
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 16 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Disaster type</label>
          <select name="disaster_type" value={form.disaster_type} onChange={handleChange}>
            <option value="flood">Flood</option>
            <option value="earthquake">Earthquake</option>
            <option value="wildfire">Wildfire</option>
            <option value="landslide">Landslide</option>
            <option value="cyclone">Cyclone</option>
            <option value="industrial_fire">Industrial Fire</option>
            <option value="storm">Storm</option>
            <option value="drought">Drought</option>
          </select>
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Location</label>
          <input
            name="location"
            placeholder="Bangalore East"
            value={form.location}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button type="button" onClick={detectLocation} disabled={locating} className="btn btn-sm">
          {locating ? "Detecting location..." : "◎ Use my location"}
        </button>

        {locationError ? <span style={{ color: "var(--danger)", fontSize: 13.5 }}>{locationError}</span> : null}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 16 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Latitude</label>
          <input
            type="number"
            step="any"
            name="latitude"
            placeholder="12.9716"
            value={form.latitude}
            onChange={handleChange}
          />
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Longitude</label>
          <input
            type="number"
            step="any"
            name="longitude"
            placeholder="77.5946"
            value={form.longitude}
            onChange={handleChange}
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 16 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">People affected</label>
          <input
            type="number"
            name="people_affected"
            value={form.people_affected}
            onChange={handleChange}
            min="0"
            required
          />
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label className="eyebrow">Injuries</label>
          <input
            type="number"
            name="injuries"
            value={form.injuries}
            onChange={handleChange}
            min="0"
            required
          />
        </div>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Other information</label>
        <textarea
          name="additional_info"
          rows="3"
          placeholder="Anything else responders should know: access routes, hazards, vulnerable people, etc."
          value={form.additional_info}
          onChange={handleChange}
        />
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <label className="eyebrow">Photos / videos (optional)</label>
        <input
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={(e) => setFiles(Array.from(e.target.files || []))}
        />
        {files.length > 0 ? (
          <div className="eyebrow" style={{ color: "var(--text-muted)" }}>{files.length} file(s) selected</div>
        ) : null}
      </div>

      {error ? <div className="banner banner-danger">{error}</div> : null}

      <button type="submit" disabled={submitting} className="btn btn-primary" style={{ padding: "13px 18px" }}>
        {submitting ? "Submitting..." : "Submit incident"}
      </button>
    </form>
  );
}