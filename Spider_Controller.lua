-- Simple Spider Controller GUI
function Main()
    gfx.init("Spider Controller", 200, 100)
    
    function Run()
        gfx.x = 20; gfx.y = 20
        if gfx.button("Enable Chain") then
            -- Logic to enable/disable plugins in the chain
            reaper.ShowMessageBox("Spider Activated", "Status", 0)
        end
        
        if gfx.getchar() ~= 27 then reaper.defer(Run) end
    end
    Run()
end

Main()
