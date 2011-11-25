//
//  CrookedViewController.m
//  Crooked
//
//  Created by Aaron Stacy on 11/25/11.
//  Copyright (c) 2011 StoredIQ. All rights reserved.
//

#import "CrookedViewController.h"

@implementation CrookedViewController
@synthesize recordButton;
@synthesize playButton;
@synthesize url = _url;
@synthesize recordSettings = _recordSettings;

- (void)didReceiveMemoryWarning
{
    [super didReceiveMemoryWarning];
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];
	// Do any additional setup after loading the view, typically from a nib.
    
    self.url = [NSURL fileURLWithPath:[NSString stringWithFormat:@"%@/recorded_audio.pcm", [[NSBundle mainBundle] resourcePath]]];
    
    self.recordSettings = [[NSMutableDictionary alloc] initWithCapacity:10];
    [self.recordSettings setObject:[NSNumber numberWithInt:kAudioFormatLinearPCM] forKey:AVFormatIDKey];
    [self.recordSettings setObject:[NSNumber numberWithFloat:44100.0] forKey:AVSampleRateKey];
    [self.recordSettings setObject:[NSNumber numberWithInt:2] forKey:AVNumberOfChannelsKey];
    [self.recordSettings setObject:[NSNumber numberWithInt:16] forKey:AVLinearPCMBitDepthKey];
    [self.recordSettings setObject:[NSNumber numberWithBool:NO] forKey:AVLinearPCMIsBigEndianKey];
    [self.recordSettings setObject:[NSNumber numberWithBool:NO] forKey:AVLinearPCMIsFloatKey];
}

- (void)viewDidUnload
{
    [self setRecordButton:nil];
    [self setPlayButton:nil];
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
    
    player = nil;
    recorder = nil;
    self.url = nil;
    self.recordSettings = nil;
}

- (void)viewWillAppear:(BOOL)animated
{
    [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated
{
    [super viewDidAppear:animated];
}

- (void)viewWillDisappear:(BOOL)animated
{
	[super viewWillDisappear:animated];
}

- (void)viewDidDisappear:(BOOL)animated
{
	[super viewDidDisappear:animated];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation != UIInterfaceOrientationPortraitUpsideDown);
}

- (IBAction)record:(id)sender {    
    if (recorder == nil) {
        [self startRecord];
        [recordButton setTitle:@"Stop Recording" forState:UIControlStateNormal];
        [playButton setTitle:@"Stop Recording and Play" forState:UIControlStateNormal];
        [playButton setEnabled:YES];
    } else {
        [self stopRecord];
        [recordButton setTitle:@"Record" forState:UIControlStateNormal];
        [playButton setTitle:@"Play" forState:UIControlStateNormal];
    }
}

- (void)startRecord {
    AVAudioSession* session = [AVAudioSession sharedInstance];
    [session setCategory:AVAudioSessionCategoryPlayback error:nil];

    NSError __autoreleasing* error = nil;
    recorder = [[AVAudioRecorder alloc] initWithURL:self.url settings:self.recordSettings error:&error];
    
    if ([recorder prepareToRecord] == YES) {
        [recorder record];
    } else {
        int errorCode = CFSwapInt32HostToBig([error code]);
        NSLog(@"ERROR: %@ [%4.4s])", [error localizedDescription], (char*)&errorCode);
    }
}

- (void)stopRecord {
    [recorder stop];
    recorder = nil;
}

- (IBAction)play:(id)sender {
    if (recorder != nil)
        [self record:recordButton];

    if (player == nil) {
        [self startPlay];
        [playButton setTitle:@"Stop Playing" forState:UIControlStateNormal];
    } else {
        [self stopPlay];
        [playButton setTitle:@"Play" forState:UIControlStateNormal];        
    }
}

- (void)startPlay {
    AVAudioSession* session = [AVAudioSession sharedInstance];
    [session setCategory:AVAudioSessionCategoryRecord error:nil];
    
    NSError __autoreleasing* error;
    player = [[AVAudioPlayer alloc] initWithContentsOfURL:self.url error:&error];
    [player setDelegate:self];
    [player play];
    
}

- (void)stopPlay {
    [player stop];
    player = nil;
}

- (void)audioPlayerDidFinishPlaying:(AVAudioPlayer*)plyr successfully:(BOOL)flag {
    [self play:playButton];
}

@end
