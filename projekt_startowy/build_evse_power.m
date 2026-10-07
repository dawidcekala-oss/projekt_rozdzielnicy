function build_evse_power()
% BUILD_EVSE_POWER  Tor mocy EVSE (1-fazowy, reprezentatywny).
% ------------------------------------------------------------------------
% Topologia (petla AC):  AC_src(+) -> K(stycznik) -> Isens -> Rload -> masa
%                        AC_src(-) -> masa
% Licznik energii:       u,i -> P=u*i -> Integrator -> /3.6e6 -> kWh
% Brama stycznika:       close = contactor_cmd AND not(fault)
%
% WAZNE konwencje:
%   * Pozycja BLOKU (add_block) = [left top right bottom] (Simulink).
%   * Porty Simscape sa fizyczne (.LConn/.RConn); sygnalowe (.Inport/.Outport).
%
% Obciazenie = Rezystor (poprawne dla AC: prad w fazie, P=Vrms^2/R).
% 3-fazowo: powiel galaz x3 (L1/L2/L3) ze wspolnym N.
%
% NIE uruchomione u autora (brak MATLAB). Bloki/parametry/pozycje sa pewne;
% OKABLOWANIE jest best-effort (porty wieloterminalowe) -> patrz [WIRING].
% Iterujemy: odpal, wyslij komunikaty [!], poprawie.
% ------------------------------------------------------------------------

mdl = 'evse_power';
if bdIsLoaded(mdl), close_system(mdl,0); end
new_system(mdl); open_system(mdl);
try set_param(mdl,'BooleanDataType','off'); catch, end   % bloki logiczne -> double (zgodnosc z PS)

A = @(n,src,pos) safeAdd([mdl '/' n],src,pos);

% ---- elementy fizyczne (Simscape Foundation: fl_lib) ----
A('AC_src','fl_lib/Electrical/Electrical Sources/AC Voltage Source',[40 200 95 280]);
setp(mdl,'AC_src',{'amplitude','325'},{'amp','325'});     % ~230 Vrms (325 V peak)
setp(mdl,'AC_src',{'frequency','50'},{'f','50'});
A('K','fl_lib/Electrical/Electrical Elements/Switch',[170 210 240 270]);
A('Isens','fl_lib/Electrical/Electrical Sensors/Current Sensor',[300 205 360 265]);
A('Rload','fl_lib/Electrical/Electrical Elements/Resistor',[440 215 500 255]);
setp(mdl,'Rload',{'R','14.4'},{});                        % ~16 A @ 230 V
A('Vsens','fl_lib/Electrical/Electrical Sensors/Voltage Sensor',[430 320 490 380]);
A('GND','fl_lib/Electrical/Electrical Elements/Electrical Reference',[300 360 360 400]);
A('Solver','nesl_utility/Solver Configuration',[40 360 130 400]);

% ---- brama stycznika: close = contactor_cmd AND not(fault) ----
A('contactor_cmd','simulink/Sources/Constant',[40 40 110 70]); setp(mdl,'contactor_cmd',{'Value','1'},{});
A('fault','simulink/Sources/Constant',[40 95 110 125]);       setp(mdl,'fault',{'Value','0'},{});
A('NOTf','simulink/Logic and Bit Operations/Logical Operator',[150 95 190 121]); setp(mdl,'NOTf',{'Operator','NOT'},{});
A('ANDg','simulink/Logic and Bit Operations/Logical Operator',[220 55 260 90]);  setp(mdl,'ANDg',{'Operator','AND'},{});
A('close2ps','nesl_utility/Simulink-PS Converter',[300 58 345 85]);

% ---- licznik energii ----
A('I2s','nesl_utility/PS-Simulink Converter',[400 150 445 174]);
A('V2s','nesl_utility/PS-Simulink Converter',[540 330 585 354]);
A('P','simulink/Math Operations/Product',[630 190 670 230]);
A('Int','simulink/Continuous/Integrator',[710 190 750 230]);
A('kWh','simulink/Math Operations/Gain',[790 190 830 230]); setp(mdl,'kWh',{'Gain','1/3.6e6'},{});
A('Disp','simulink/Sinks/Display',[870 195 930 225]);
A('Scope','simulink/Sinks/Scope',[870 260 910 300]);

% ---- okablowanie (best-effort) ----
W = @(b1,p1,i1,b2,p2,i2) wire(mdl,b1,p1,i1,b2,p2,i2);
% petla mocy (lewo->prawo)
W('AC_src','RConn',1,'K','LConn',1);
W('K','RConn',1,'Isens','LConn',1);
W('Isens','RConn',1,'Rload','LConn',1);
W('Rload','RConn',1,'GND','LConn',1);
W('AC_src','LConn',1,'GND','LConn',1);
W('Solver','RConn',1,'GND','LConn',1);
% pomiar napiecia rownolegle do obciazenia
W('Vsens','LConn',1,'Rload','LConn',1);
W('Vsens','RConn',1,'GND','LConn',1);
% sterowanie stycznikiem
W('contactor_cmd','Outport',1,'ANDg','Inport',1);
W('fault','Outport',1,'NOTf','Inport',1);
W('NOTf','Outport',1,'ANDg','Inport',2);
W('ANDg','Outport',1,'close2ps','Inport',1);
W('close2ps','RConn',1,'K','LConn',2);          % wejscie sterujace switcha (PS)
% licznik: czujniki -> PS-Simulink -> Product -> calka -> kWh
W('Isens','RConn',2,'I2s','Inport',1);          % PS wyjscie pradu (jesli inny indeks: patrz [WIRING])
W('Vsens','RConn',2,'V2s','Inport',1);          % PS wyjscie napiecia
W('I2s','Outport',1,'P','Inport',1);
W('V2s','Outport',1,'P','Inport',2);
W('P','Outport',1,'Int','Inport',1);
W('Int','Outport',1,'kWh','Inport',1);
W('kWh','Outport',1,'Disp','Inport',1);
W('kWh','Outport',1,'Scope','Inport',1);

wiringList();
try Simulink.BlockDiagram.arrangeSystem(mdl); catch, end
fprintf(['\nTor mocy "%s" gotowy. Ustaw fault=1, by zobaczyc weto (stycznik otwarty).\n' ...
         'Polaczenia z [!] dokoncz wg listy [WIRING] (porty wieloterminalowe).\n'], mdl);
end

% ===================== helpery =====================
function safeAdd(dst,src,pos)
  try, add_block(src,dst,'Position',pos);
  catch e, fprintf('  [!] add %s (%s): %s\n',dst,src,e.message); end
end

function setp(mdl,blk,pref,alt)   % probuj nazwe glowna, potem alternatywna
  ok=false;
  try, set_param([mdl '/' blk],pref{1},pref{2}); ok=true; catch, end
  if ~ok && ~isempty(alt)
    try, set_param([mdl '/' blk],alt{1},alt{2}); catch, end
  end
end

function wire(mdl,b1,p1,i1,b2,p2,i2)
  try
    h1=get_param([mdl '/' b1],'PortHandles');
    h2=get_param([mdl '/' b2],'PortHandles');
    add_line(mdl,h1.(p1)(i1),h2.(p2)(i2),'autorouting','on');
  catch e
    fprintf('  [!] %s.%s(%d) -> %s.%s(%d): %s\n',b1,p1,i1,b2,p2,i2,e.message);
  end
end

function wiringList()
  fprintf(['\n[WIRING] tor mocy (porty fizyczne Simscape):\n' ...
   '  AC_src(+) -- K(L) ; K(R) -- Isens(in) ; Isens(out) -- Rload(L)\n' ...
   '  Rload(R) -- GND ; AC_src(-) -- GND ; Solver -- GND ; Vsens(+) -- wezel Rload(L) ; Vsens(-) -- GND\n' ...
   '  K(sterowanie PS) <- close2ps ; Isens(I, PS) -> I2s ; Vsens(V, PS) -> V2s\n' ...
   '  contactor_cmd -> ANDg(1) ; fault -> NOTf -> ANDg(2) ; ANDg -> close2ps\n' ...
   '  I2s -> P(1) ; V2s -> P(2) ; P -> Int -> kWh -> Disp & Scope\n']);
end
