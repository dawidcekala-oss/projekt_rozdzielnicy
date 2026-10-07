<!--
  Szablon ekranu Shelly dla funkcji "Portable EVSE" (web_template z portalu x.shelly.cloud,
  pobrany 2026-09-29). Z niego portal generuje web.svc.svelte.
  Znane bledy szablonu:
    - fazy czyta z phase_info.displayValue zamiast z wartosci, wiec prad faz zawsze "N/A A";
    - moc podpisuje "kW", a pole phase_info.total_power jest w W.
-->
<script lang="ts">
  export let service: any;

  const {
    state,
    mode,
    current_limit,
    phase_info,
    session_energy,
    session_duration,
  } = service.components.get();

  const SLIDER_COLOR = '#21bf54';
  const DEBOUNCE_UPDATE_TIME = 500;

  const stateValue = state.value;
  const modeValue = mode.displayValue;
  const modeName = mode.componentName;
  const currentVal = current_limit.value;
  const currentUnit = current_limit.unit;
  const currentTitle = current_limit.componentName;
  const currentConfig = current_limit.config;
  const phaseInfoValue = phase_info.displayValue;
  const phaseInfoName = phase_info.componentName;

  const PHASE_LIST = [
    { title: 'Phase A', key: 'phase_a' },
    { title: 'Phase B', key: 'phase_b' },
    { title: 'Phase C', key: 'phase_c' },
  ];

  $: totalPower = $phaseInfoValue?.total_power ?? 0;
  $: totalEnergy = $phaseInfoValue?.total_act_energy ?? 0;
  const sessionEnergyValue = session_energy.displayValue;
  const sessionEnergyName = session_energy.componentName;
  const sessionDurationValue = session_duration.displayValue;
  const sessionDurationName = session_duration.componentName;

  $: scalePlateArr = [$currentConfig.min, $currentConfig.max];

  let sliderCounter = 0;
  const currentLimitSlider = `slider-${sliderCounter++}`;
  let currentLimitSliderValue = $currentVal;
  let currentLimitDebounceTimer: ReturnType<typeof setTimeout> | undefined;

  function updateCurrentLimitValue(newValue: number) {
    clearTimeout(currentLimitDebounceTimer);
    currentLimitDebounceTimer = setTimeout(() => {
      current_limit.set(newValue);
    }, DEBOUNCE_UPDATE_TIME);
  }

  $: currentLimitSliderValue = $currentVal;
  $: currentLimitPosition =
    (($currentVal - $currentConfig.min) * 100) /
    ($currentConfig.max - $currentConfig.min);
  $: currentLimitSliderStyle = `left: calc(${currentLimitPosition}% + (${8 - currentLimitPosition * 0.2}px));`;
  $: currentLimitGradient = `linear-gradient(90deg, ${SLIDER_COLOR} ${currentLimitPosition}%, var(--background-color) ${currentLimitPosition}%)`;
</script>

<div
  style="--cols: 2; --gap: 1rem; display: grid; grid-gap: var(--gap); grid-template-columns: repeat(var(--cols), 1fr);"
>
  <!-- Enable/Disable Charging -->
  <section class="card">
    <header>
      <div class="info">
        <div class="header">
          <div class="card-header">
            <span class="primary">Charging</span>
            <span class="secondary">{$stateValue ? 'Enabled' : 'Disabled'}</span
            >
          </div>
        </div>
      </div>
      <div class="controls">
        <button
          class="ui-button"
          class:active={$stateValue}
          on:click={() => state.set(!$stateValue)}
        >
          <svg
            viewBox="0 0 24 24"
            width="20px"
            height="20px"
            stroke="var(--primary)"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
            <line
              x1="12"
              y1="2"
              x2="12"
              y2="12"
            />
          </svg>
        </button>
      </div>
    </header>
  </section>

  <!-- Charger Mode -->
  <section class="card">
    <header>
      <div class="info">
        <div class="header">
          <div class="card-header">
            <span class="primary">{$modeName}</span>
            <span class="secondary">{$modeValue}</span>
          </div>
        </div>
      </div>
    </header>
  </section>

  <!-- Phase Info -->
  <div class="phase-info-wrapper">
    <section class="phase-card">
      <header>
        <div class="info">
          <div class="header">
            <div class="card-header">
              <span class="primary">{$phaseInfoName}</span>
            </div>
          </div>
        </div>
      </header>
    </section>

    <div class="phase-grid">
      {#each PHASE_LIST as { key, title }}
        <section class="card">
          <header>
            <div class="info">
              <div class="header">
                <div class="card-header">
                  <span class="primary">{title}</span>
                  <span class="secondary"
                    >{$phaseInfoValue?.[key]?.current ?? 'N/A'} A</span
                  >
                </div>
              </div>
            </div>
          </header>
        </section>
      {/each}
    </div>

    <div class="phase-grid">
      <section class="card">
        <header>
          <div class="info">
            <div class="header">
              <div class="card-header">
                <span class="primary">Power</span>
                <span class="secondary">{totalPower} kW</span>
              </div>
            </div>
          </div>
        </header>
      </section>

      <section class="card">
        <header>
          <div class="info">
            <div class="header">
              <div class="card-header">
                <span class="primary">Total Active Energy</span>
                <span class="secondary">{totalEnergy} kWh</span>
              </div>
            </div>
          </div>
        </header>
      </section>
    </div>
  </div>

  <!-- Session Energy -->
  <section class="card">
    <header>
      <div class="info">
        <div class="header">
          <div class="card-header">
            <span class="primary">{$sessionEnergyName}</span>
            <span class="secondary">{$sessionEnergyValue}</span>
          </div>
        </div>
      </div>
    </header>
  </section>

  <!-- Session Duration -->
  <section class="card">
    <header>
      <div class="info">
        <div class="header">
          <div class="card-header">
            <span class="primary">{$sessionDurationName}</span>
            <span class="secondary">{$sessionDurationValue}</span>
          </div>
        </div>
      </div>
    </header>
  </section>
</div>

<!-- Current Limit Slider -->
<section class="card">
  <header>
    <div class="info">
      <div class="header">
        <div class="card-header">
          <span class="primary">{$currentTitle}</span>
          <span class="secondary">{$currentVal} {$currentUnit}</span>
        </div>
      </div>
    </div>
  </header>

  <div class="slider-wrapper">
    <div style="position: relative;">
      <input
        type="range"
        id={currentLimitSlider}
        bind:value={currentLimitSliderValue}
        on:change={() => updateCurrentLimitValue(currentLimitSliderValue)}
        on:input={() => {
          updateCurrentLimitValue(currentLimitSliderValue);
        }}
        min={$currentConfig.min}
        max={$currentConfig.max}
        step={1}
        style="--gradient: {currentLimitGradient};"
      />
      <output style={currentLimitSliderStyle}
        >{currentLimitSliderValue} {$currentUnit}</output
      >
    </div>

    <div class="scaleplate">
      {#each scalePlateArr as scaleNum}
        <p>{scaleNum}</p>
      {/each}
    </div>
  </div>
</section>

<style>
  .card {
    background-color: var(--background-opacity);
    border-radius: var(--card-radius);
    display: flex;
    flex-wrap: wrap;
    flex-direction: row;
    position: relative;
    margin: 0.15rem 0;
    padding: 0.5rem;
  }

  header {
    display: flex;
    flex-direction: row;
    width: 100%;
    gap: 1rem;
    align-items: center;
    margin: 0 0.4rem;
    padding: 0.5rem 0;
    height: fit-content;
  }

  .info {
    display: flex;
    align-items: center;
  }

  .header {
    width: fit-content;
  }

  .controls {
    font-size: var(--medium-font);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex: 1;
  }

  .card-header {
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    margin-left: 0.5rem;
  }

  .primary {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
  }

  .secondary {
    font-size: 13px;
    font-weight: 400;
    color: #bbc6ce;
  }

  .ui-button {
    all: unset;
    background-color: var(--color);
    width: fit-content;
    border-radius: 5rem;
    border: 0.4rem solid var(--secondary);
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.5rem 3rem;
  }

  .ui-button.active {
    border-color: var(--primary);
  }

  .slider-wrapper {
    flex: auto;
    padding: 0.5rem 0;
    margin: 0 0.4rem;
  }

  input[type='range'] {
    margin: 0.4rem 0 !important;
    width: 100%;
  }

  input[type='range']::-moz-range-track {
    background: var(--gradient);
  }

  input[type='range']::-webkit-slider-runnable-track {
    background: var(--gradient);
  }

  input[type='range']::-moz-range-thumb {
    border: unset !important;
  }

  input[type='range']::-webkit-slider-thumb {
    border: unset !important;
  }

  output {
    display: none;
    background-color: var(--background-color);
    padding: 4px 12px;
    position: absolute;
    border-radius: 4px;
    left: 50%;
    top: 100%;
    transform: translateX(-50%);
    z-index: 100;
  }

  input[type='range']:hover + output {
    display: block;
  }

  .scaleplate {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    margin-top: 0.5rem;
  }

  .scaleplate p {
    margin: 0;
    font-size: 12px;
  }

  @media (max-width: 1300px) {
    div[style*='--cols'] {
      grid-template-columns: repeat(min(2, var(--cols)), 1fr);
    }
  }

  @media (max-width: 800px) {
    div[style*='--cols'] {
      grid-template-columns: repeat(min(1, var(--cols)), 1fr);
    }
  }

  .phase-info-wrapper {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin: 1rem 0;
  }

  .phase-card {
    background-color: var(--background-opacity);
    border-radius: var(--card-radius);
    display: flex;
    flex-wrap: wrap;
    flex-direction: row;
    position: relative;
    margin: 0.15rem 0;
    padding: 0.5rem;
    width: 100%;
  }

  .phase-grid {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    column-gap: 1rem;
  }

  @media (max-width: 800px) {
    .phase-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
