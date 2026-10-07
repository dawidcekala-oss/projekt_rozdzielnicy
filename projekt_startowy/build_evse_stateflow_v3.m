function build_evse_stateflow_v3()
% BUILD_EVSE_STATEFLOW_V2  (czysta, poprawna, szczegolowa wersja)
% ------------------------------------------------------------------------
% Buduje dwie karty Stateflow modelu cyfrowego blizniaka EVSE:
%   1) Emulator_auta   - aktor: samochod (strona auta handshake'u IEC 61851)
%   2) Wzorzec_EVSE    - aktor: ladowarka, w architekturze 3 petli
%
% Poprawki wzgledem v1 (zrodlo bledow skladni):
%   * Etykiety stanow tylko: <nazwa> + linie akcji (entry:/during:/exit:).
%     ZADNYCH linii opisowych w etykiecie (to one powodowaly parse error).
%     Opisy -> adnotacje (Stateflow.Annotation).
%   * Pelna hierarchia: superstan "Operating" (petla 2: handshake) +
%     weto bezpieczenstwa jako JEDNO grupowe przejscie Operating->Tripped
%     (poprawny idiom; zamiast kruchego parallel-AND).
%   * Czysty uklad: odstepy + jawne zegary (SourceOClock/DestinationOClock).
%
% Warunki napiecia CP (IEC 61851, mierzone na wezle CP):
%   A ~ +12V (cp>10.5) | B ~ +9V (7.5..10.5) | C ~ +6V (4.5..7.5) |
%   D ~ +3V (1.5..4.5, ladowanie z wentylacja) | E/F <=0 (blad).
%
% UWAGA: nie uruchomione u autora (brak MATLAB). Powinno parsowac sie czysto.
% Po uruchomieniu otworz karty; ewentualne komunikaty wskaza stan/przejscie.
% ------------------------------------------------------------------------

mdl = 'evse_stateflow';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);

build_emulator(mdl);
build_golden(mdl);

try, sf('Open', mdl); catch, end
fprintf('Gotowe: model "%s" z kartami Emulator_auta i Wzorzec_EVSE.\n', mdl);
end

% ======================= KARTA 1: EMULATOR AUTA =======================
function build_emulator(mdl)
nm = 'Emulator_auta';
ch = getChart(mdl, nm, [40 40 360 220]);

% --- slownik danych (porty wejscia/wyjscia) ---
addData(ch,'cmd','Input'); addData(ch,'I_offer','Input');           % 0=unplug 1=connect 2=ready 3=stop 4=ventilate
addData(ch,'fault_inject','Input');  % 1=wstrzyknij usterke
addData(ch,'StateC','Output');       % 1 => dolaczony R3 (stan C, ~6V)
addData(ch,'diode_on','Output');     % 1 => dioda wpieta (brak = usterka)
addData(ch,'i_demand','Output');     % prad pobierany w stanie C/D [A]

% --- stany (etykiety parse-safe: nazwa + entry:) ---
sA = addState(ch, sprintf('A_Unplugged\nentry: diode_on=0; StateC=0; i_demand=0;'), [ 60 70 190 80]);
sB = addState(ch, sprintf('B_Connected\nentry: diode_on=1; StateC=0; i_demand=0;'), [330 70 190 80]);
sC = addState(ch, sprintf('C_Ready\nentry: StateC=1; i_demand=min(I_offer,32);'),                 [600 70 190 80]);
sD = addState(ch, sprintf('D_Ventilation\nentry: StateC=1; i_demand=10;'),           [600 230 190 80]);
sF = addState(ch, sprintf('Fault\nentry: diode_on=0; StateC=0; i_demand=0;'),        [330 230 190 80]);

addDefault(ch, sA, 0);

addTrans(ch, sA, sB, '[cmd==1]', 3, 9);
addTrans(ch, sB, sC, '[cmd==2]', 3, 9);
addTrans(ch, sC, sB, '[cmd==3]', 10, 2);
addTrans(ch, sC, sD, '[cmd==4]', 6, 12);
addTrans(ch, sD, sC, '[cmd==2]', 9, 6);
addTrans(ch, sB, sA, '[cmd==0]', 8, 4);
addTrans(ch, sC, sA, '[cmd==0]', 7, 1);
addTrans(ch, sB, sF, '[fault_inject==1]', 6, 12);
addTrans(ch, sF, sA, '[fault_inject==0]', 9, 5);
  addTrans(ch, sD, sA, '[cmd==0]', 7, 4);            % v3: odpiecie z wentylacji
  addTrans(ch, sC, sF, '[fault_inject==1]', 6, 12); % v3: usterka w trakcie ladowania

addNote(ch, 'Emulator auta: pasywny elektrycznie - wybiera rezystory/diode.', [60 20]);
end

% ======================= KARTA 2: WZORZEC EVSE =======================
% Architektura 3 petli:
%   petla 2 (sterowanie) = superstan Operating: Idle/Detected/Charging/Ventilation
%   petla 1 (bezpieczenstwo) = weto: Operating->Tripped [fault_p1]
%   petla 3 (aplikacja) = dane wejsciowe auth_ok / I_avail (limity, autoryzacja)
function build_golden(mdl)
nm = 'Wzorzec_EVSE';
ch = getChart(mdl, nm, [40 320 360 540]);

% --- slownik danych ---
addData(ch,'cp_voltage','Input');    % napiecie CP [V] - jedyne z granicy auto<->ladowarka
addData(ch,'auth_ok','Input');       % petla 3: autoryzacja (RFID/limit)
addData(ch,'fault_p1','Input');      % petla 1: usterka (RCD/PE/zwarcie/sklejenie)
addData(ch,'I_avail','Input');       % limit pradu [A] (instalacja/PP/DLB) - petla 3
addData(ch,'duty','Output');         % wypelnienie PWM [%]
addData(ch,'contactor_cmd','Output');% zadanie zamkniecia stycznika (1/0)
addData(ch,'I_offer','Output');      % prad oferowany [A]
addData(ch,'pwm_on','Output');       % 1 => PWM aktywny; 0 => stale +12V (standby)

% --- superstan Operating (petla 2) ---
sOp = addState(ch, 'Operating', [40 70 900 380]);

% substany WEWNATRZ Operating (geometria => hierarchia)
sIdle = addState(ch, sprintf('Idle\nentry: pwm_on=0; duty=0; contactor_cmd=0; I_offer=0;'), [ 90 170 210 120]);
sDet  = addState(ch, sprintf('Detected\nentry: pwm_on=1; I_offer=I_avail; duty=max(10,min(85,I_offer/0.6)); contactor_cmd=0;'), [380 170 250 150]);
sChg  = addState(ch, sprintf('Charging\nentry: contactor_cmd=1;\nduring: I_offer=I_avail; duty=max(10,min(85,I_offer/0.6));'), [710 170 210 130]);
sVent = addState(ch, sprintf('Ventilation\nentry: contactor_cmd=1;'), [710 330 210 90]);

addDefault(ch, sIdle, 0);

% przejscia handshake (petla 2) - jawne zegary, by sie nie nakladaly
addTrans(ch, sIdle, sDet,  '[cp_voltage>7.5 && cp_voltage<10.5 && I_avail>0]', 3, 9);            % A->B
addTrans(ch, sDet,  sChg,  '[cp_voltage>4.5 && cp_voltage<7.5 && auth_ok==1]', 3, 9);% B->C
addTrans(ch, sChg,  sDet,  '[cp_voltage>7.5 && cp_voltage<10.5]', 11, 1);           % C->B
addTrans(ch, sDet,  sIdle, '[cp_voltage>10.5]', 8, 4);                              % ->A (odpiecie)
addTrans(ch, sChg,  sVent, '[cp_voltage>1.5 && cp_voltage<4.5]', 6, 12);            % C->D (wentylacja)
addTrans(ch, sVent, sChg,  '[cp_voltage>4.5 && cp_voltage<7.5]', 9, 6);             % D->C

% --- stan bezpieczny i weto petli 1 (poza Operating) ---
sTrip = addState(ch, sprintf('Tripped\nentry: contactor_cmd=0; pwm_on=0; duty=0;'), [380 500 250 110]);
addTrans(ch, sOp,   sTrip, '[fault_p1==1 || cp_voltage<1.5]', 6, 12);   % weto: z dowolnego substanu Operating
addTrans(ch, sTrip, sOp,   '[fault_p1==0]', 9, 7);    % reset -> wejscie do Operating (default=Idle)

addNote(ch, 'Petla 3 (aplikacja): auth_ok, I_avail = nastawy/limity (RFID, DLB, harmonogram).', [40 30]);
addNote(ch, 'Petla 1 (bezpieczenstwo): fault_p1 = OR(RCD, PE, zwarcie CP, sklejenie). Weto nadrzedne.', [380 630]);
addNote(ch, 'I_offer/duty: duty=max(10,min(85,I_offer/0.6)) (10-85%). DLB: during w Charging sledzi I_avail.', [710 640]);
end

% ======================= HELPERY (Stateflow API) =======================
function ch = getChart(mdl,name,pos)
  add_block('sflib/Chart',[mdl '/' name],'Position',pos);
  rt = sfroot; cs = rt.find('-isa','Stateflow.Chart'); ch = [];
  for k = 1:numel(cs)
    if strcmp(cs(k).Name,name), ch = cs(k); end
  end
end

function d = addData(ch,name,scope)
  d = Stateflow.Data(ch); d.Name = name; d.Scope = scope;
end

function s = addState(ch,label,pos)
  s = Stateflow.State(ch); s.LabelString = label; s.Position = pos;
end

function t = addTrans(ch,src,dst,lbl,sClk,dClk)
  t = Stateflow.Transition(ch); t.Source = src; t.Destination = dst;
  if ~isempty(lbl), t.LabelString = lbl; end
  if nargin>=5 && ~isempty(sClk), try t.SourceOClock = sClk; catch, end; end
  if nargin>=6 && ~isempty(dClk), try t.DestinationOClock = dClk; catch, end; end
end

function addDefault(ch,dst,clk)
  t = Stateflow.Transition(ch); t.Destination = dst; p = dst.Position;
  try t.DestinationOClock = clk; catch, end
  try t.SourceEndPoint = [p(1)+p(3)/2, p(2)-32]; catch, end
  try t.MidPoint       = [p(1)+p(3)/2, p(2)-16]; catch, end
end

function addNote(ch,txt,pos)
  try a = Stateflow.Annotation(ch); a.Text = txt; a.Position = [pos(1) pos(2) 360 24]; catch, end
end
